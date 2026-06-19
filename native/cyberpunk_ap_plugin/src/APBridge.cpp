#include "APBridge.hpp"

#include <cstdio>

namespace
{
std::string NormalizeSlotDataRawString(std::string rawValue)
{
    while (!rawValue.empty() && (rawValue.back() == '\n' || rawValue.back() == '\r'))
    {
        rawValue.pop_back();
    }

    if (rawValue.size() >= 2 && rawValue.front() == '"' && rawValue.back() == '"')
    {
        rawValue = rawValue.substr(1, rawValue.size() - 2);
        std::string unescaped;
        unescaped.reserve(rawValue.size());
        bool escaping = false;
        for (char current : rawValue)
        {
            if (escaping)
            {
                switch (current)
                {
                case 'n':
                    unescaped.push_back('\n');
                    break;
                case 'r':
                    unescaped.push_back('\r');
                    break;
                case 't':
                    unescaped.push_back('\t');
                    break;
                case '\\':
                    unescaped.push_back('\\');
                    break;
                case '"':
                    unescaped.push_back('"');
                    break;
                default:
                    unescaped.push_back(current);
                    break;
                }
                escaping = false;
                continue;
            }

            if (current == '\\')
            {
                escaping = true;
                continue;
            }

            unescaped.push_back(current);
        }
        rawValue = unescaped;
    }

    return rawValue;
}
} // namespace

namespace CyberpunkArchipelago
{
APBridge& APBridge::Get()
{
    static APBridge s_instance;
    return s_instance;
}

bool APBridge::Initialize(const std::string& serverAddress,
                          const std::string& gameName,
                          const std::string& slotName,
                          const std::string& password)
{
    if (serverAddress.empty() || gameName.empty() || slotName.empty())
    {
        return false;
    }

    std::lock_guard<std::mutex> lock(m_mutex);
    if (m_initialized && AP_IsInit())
    {
        return true;
    }

    AP_Init(serverAddress.c_str(), gameName.c_str(), slotName.c_str(), password.c_str());
    AP_SetItemClearCallback(&APBridge::OnItemClear);
    AP_SetItemRecvCallback(&APBridge::OnItemReceived);
    AP_SetLocationCheckedCallback(&APBridge::OnLocationChecked);
    AP_SetDeathLinkSupported(true);
    AP_SetDeathLinkRecvCallback(&APBridge::OnDeathLinkReceived);
    AP_RegisterSlotDataIntCallback("death_link", &APBridge::OnSlotDataDeathLink);
    AP_RegisterSlotDataIntCallback("restrict_by_major_district", &APBridge::OnSlotDataRestrictByMajorDistrict);
    AP_RegisterSlotDataIntCallback("restrict_by_sub_district", &APBridge::OnSlotDataRestrictBySubDistrict);
    AP_RegisterSlotDataIntCallback("district_token_gated_major_mask", &APBridge::OnSlotDataDistrictTokenGatedMajorMask);
    AP_RegisterSlotDataIntCallback("weapon_restriction_type", &APBridge::OnSlotDataWeaponRestrictionType);
    AP_RegisterSlotDataIntCallback("weapon_restrict_pistol", &APBridge::OnSlotDataWeaponRestrictPistol);
    AP_RegisterSlotDataIntCallback("weapon_restrict_melee", &APBridge::OnSlotDataWeaponRestrictMelee);
    AP_RegisterSlotDataIntCallback("weapon_restrict_rifle", &APBridge::OnSlotDataWeaponRestrictRifle);
    AP_RegisterSlotDataIntCallback("weapon_restrict_sniper", &APBridge::OnSlotDataWeaponRestrictSniper);
    AP_RegisterSlotDataIntCallback("weapon_restrict_lmg", &APBridge::OnSlotDataWeaponRestrictLmg);
    AP_RegisterSlotDataIntCallback("weapon_restrict_shotgun", &APBridge::OnSlotDataWeaponRestrictShotgun);
    AP_RegisterSlotDataIntCallback("weapon_restrict_smg", &APBridge::OnSlotDataWeaponRestrictSmg);
    AP_RegisterSlotDataIntCallback("vendor_sanity", &APBridge::OnSlotDataVendorSanity);
    AP_RegisterSlotDataRawCallback("vendor_sanity_stock", &APBridge::OnSlotDataVendorSanityStock);

    // AP_Init() is void and has no synchronous failure path; AP_IsInit() only
    // returns true after AP_Start() is called, so we track init state ourselves.
    m_initialized = true;
    m_started = false;
    return true;
}

bool APBridge::Connect()
{
    std::lock_guard<std::mutex> lock(m_mutex);
    // AP_IsInit() is only true AFTER AP_Start() has been called, so we must not
    // gate AP_Start() on AP_IsInit(). Guard only on our own m_initialized flag.
    if (!m_initialized)
    {
        return false;
    }

    if (!m_started)
    {
        AP_Start();
        m_started = true;
    }

    return true;
}

void APBridge::Shutdown()
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (AP_IsInit())
    {
        AP_Shutdown();
    }

    m_initialized = false;
    m_started = false;
    m_deathLinkPending = false;
    m_deathLinkEnabled = false;
    m_restrictByMajorDistrict = false;
    m_restrictBySubDistrict = false;
    m_districtTokenGatedMajorMask = 0;
    m_weaponRestrictionType = 0;
    m_weaponRestrictPistol = false;
    m_weaponRestrictMelee = false;
    m_weaponRestrictRifle = false;
    m_weaponRestrictSniper = false;
    m_weaponRestrictLmg = false;
    m_weaponRestrictShotgun = false;
    m_weaponRestrictSmg = false;
    m_vendorSanityEnabled = false;
    m_vendorSanityStockLine.clear();
    std::queue<ReceivedItemEntry> empty;
    m_receivedItems.swap(empty);
    m_lastPolledNetworkIndex = -1;
    m_lastPolledShouldNotify = false;
    m_lastPolledNotifySender.clear();
    m_lastPolledNotifyDisplayName.clear();
}

bool APBridge::IsReady() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return IsReadyLocked();
}

bool APBridge::IsReadyLocked() const
{
    return m_initialized && AP_IsInit();
}

bool APBridge::IsConnected() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!m_initialized) return false;
    const auto status = AP_GetConnectionStatus();
    return status == AP_ConnectionStatus::Connected || status == AP_ConnectionStatus::Authenticated;
}

int32_t APBridge::GetConnectionStatus() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!m_initialized) return 0;
    return static_cast<int32_t>(AP_GetConnectionStatus());
}

std::string APBridge::GetLastConnectionError() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!m_initialized) return "";
    const char* error = AP_GetLastConnectionError();
    if (error)
    {
        return error;
    }

    return "";
}

bool APBridge::SendLocationCheck(int64_t locationId)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!IsReadyLocked())
    {
        return false;
    }

    AP_SendItem(locationId);
    return true;
}

bool APBridge::SendDeathLink(const std::string& cause)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!IsReadyLocked())
    {
        std::fprintf(stderr, "CyberpunkAP: SendDeathLink rejected — bridge not ready\n");
        return false;
    }

    std::fprintf(stderr, "CyberpunkAP: SendDeathLink invoking APCpp (cause=\"%s\")\n", cause.c_str());
    AP_DeathLinkSend(cause);
    return true;
}

bool APBridge::SendSay(const std::string& text)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!IsReadyLocked())
    {
        return false;
    }

    AP_Say(text);
    return true;
}

bool APBridge::StoryComplete()
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!IsReadyLocked())
    {
        return false;
    }

    AP_StoryComplete();
    return true;
}

bool APBridge::PollReceivedItemId(int64_t& outItemId)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_lastPolledNetworkIndex = -1;
    m_lastPolledShouldNotify = false;
    m_lastPolledNotifySender.clear();
    m_lastPolledNotifyDisplayName.clear();

    if (m_receivedItems.empty())
    {
        return false;
    }

    const ReceivedItemEntry entry = m_receivedItems.front();
    m_receivedItems.pop();
    outItemId = entry.itemId;
    m_lastPolledNetworkIndex = entry.networkIndex;
    m_lastPolledShouldNotify = entry.shouldNotify;

    m_lastPolledNotifySender = entry.senderName;
    m_lastPolledNotifyDisplayName = entry.itemDisplayName;
    return true;
}

int32_t APBridge::GetPolledItemNetworkIndex() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_lastPolledNetworkIndex;
}

bool APBridge::GetPolledItemShouldNotify() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_lastPolledShouldNotify;
}

std::string APBridge::GetPolledItemNotifySender() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_lastPolledNotifySender;
}

std::string APBridge::GetPolledItemNotifyDisplayName() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_lastPolledNotifyDisplayName;
}

bool APBridge::IsDeathLinkPending() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_deathLinkPending;
}

void APBridge::ClearDeathLink()
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (m_deathLinkPending)
    {
        AP_DeathLinkClear();
        m_deathLinkPending = false;
    }
}

bool APBridge::GetDeathLinkEnabled() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_deathLinkEnabled;
}

bool APBridge::GetRestrictByMajorDistrict() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_restrictByMajorDistrict;
}

bool APBridge::GetRestrictBySubDistrict() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_restrictBySubDistrict;
}

int32_t APBridge::GetDistrictTokenGatedMajorMask() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_districtTokenGatedMajorMask;
}

int32_t APBridge::GetWeaponRestrictionType() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictionType;
}

bool APBridge::GetWeaponRestrictPistol() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictPistol;
}

bool APBridge::GetWeaponRestrictMelee() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictMelee;
}

bool APBridge::GetWeaponRestrictRifle() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictRifle;
}

bool APBridge::GetWeaponRestrictSniper() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictSniper;
}

bool APBridge::GetWeaponRestrictLmg() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictLmg;
}

bool APBridge::GetWeaponRestrictShotgun() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictShotgun;
}

bool APBridge::GetWeaponRestrictSmg() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_weaponRestrictSmg;
}

bool APBridge::GetVendorSanityEnabled() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_vendorSanityEnabled;
}

std::string APBridge::GetVendorSanityStockLine() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_vendorSanityStockLine;
}

void APBridge::OnItemClear()
{
    std::lock_guard<std::mutex> lock(APBridge::Get().m_mutex);
    std::queue<ReceivedItemEntry> empty;
    APBridge::Get().m_receivedItems.swap(empty);
    APBridge::Get().m_lastPolledNetworkIndex = -1;
    APBridge::Get().m_lastPolledShouldNotify = false;
    APBridge::Get().m_lastPolledNotifySender.clear();
    APBridge::Get().m_lastPolledNotifyDisplayName.clear();
}

void APBridge::OnItemReceived(int64_t itemId, std::string senderName, std::string itemDisplayName, bool notify, int32_t networkIndex)
{
    APBridge::Get().PushItem(itemId, senderName, itemDisplayName, notify, networkIndex);
}

void APBridge::OnLocationChecked(int64_t)
{
}

void APBridge::OnDeathLinkReceived()
{
    std::fprintf(stderr, "CyberpunkAP: inbound DeathLink received — marked pending\n");
    APBridge::Get().MarkDeathLinkPending();
}

void APBridge::OnSlotDataDeathLink(int value)
{
    std::fprintf(stderr, "CyberpunkAP: slot_data death_link=%d\n", value);
    APBridge::Get().SetDeathLinkEnabled(value != 0);
}

void APBridge::OnSlotDataRestrictByMajorDistrict(int value)
{
    APBridge::Get().SetRestrictByMajorDistrict(value != 0);
}

void APBridge::OnSlotDataRestrictBySubDistrict(int value)
{
    APBridge::Get().SetRestrictBySubDistrict(value != 0);
}

void APBridge::OnSlotDataDistrictTokenGatedMajorMask(int value)
{
    APBridge::Get().SetDistrictTokenGatedMajorMask(value);
}

void APBridge::OnSlotDataWeaponRestrictionType(int value)
{
    APBridge::Get().SetWeaponRestrictionType(value);
}

void APBridge::OnSlotDataWeaponRestrictPistol(int value)
{
    APBridge::Get().SetWeaponRestrictPistol(value != 0);
}

void APBridge::OnSlotDataWeaponRestrictMelee(int value)
{
    APBridge::Get().SetWeaponRestrictMelee(value != 0);
}

void APBridge::OnSlotDataWeaponRestrictRifle(int value)
{
    APBridge::Get().SetWeaponRestrictRifle(value != 0);
}

void APBridge::OnSlotDataWeaponRestrictSniper(int value)
{
    APBridge::Get().SetWeaponRestrictSniper(value != 0);
}

void APBridge::OnSlotDataWeaponRestrictLmg(int value)
{
    APBridge::Get().SetWeaponRestrictLmg(value != 0);
}

void APBridge::OnSlotDataWeaponRestrictShotgun(int value)
{
    APBridge::Get().SetWeaponRestrictShotgun(value != 0);
}

void APBridge::OnSlotDataWeaponRestrictSmg(int value)
{
    APBridge::Get().SetWeaponRestrictSmg(value != 0);
}

void APBridge::OnSlotDataVendorSanity(int value)
{
    APBridge::Get().SetVendorSanityEnabled(value != 0);
}

void APBridge::OnSlotDataVendorSanityStock(std::string value)
{
    APBridge::Get().SetVendorSanityStockLine(value);
}

void APBridge::PushItem(int64_t itemId, const std::string& senderName, const std::string& itemDisplayName, bool shouldNotify, int32_t networkIndex)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_receivedItems.push({itemId, senderName, itemDisplayName, shouldNotify, networkIndex});
}

void APBridge::MarkDeathLinkPending()
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_deathLinkPending = true;
}

void APBridge::SetRestrictByMajorDistrict(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_restrictByMajorDistrict = value;
}

void APBridge::SetDeathLinkEnabled(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_deathLinkEnabled = value;
}

void APBridge::SetRestrictBySubDistrict(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_restrictBySubDistrict = value;
}

void APBridge::SetDistrictTokenGatedMajorMask(int32_t value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_districtTokenGatedMajorMask = value;
}

void APBridge::SetWeaponRestrictionType(int32_t value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictionType = value;
}

void APBridge::SetWeaponRestrictPistol(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictPistol = value;
}

void APBridge::SetWeaponRestrictMelee(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictMelee = value;
}

void APBridge::SetWeaponRestrictRifle(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictRifle = value;
}

void APBridge::SetWeaponRestrictSniper(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictSniper = value;
}

void APBridge::SetWeaponRestrictLmg(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictLmg = value;
}

void APBridge::SetWeaponRestrictShotgun(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictShotgun = value;
}

void APBridge::SetWeaponRestrictSmg(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_weaponRestrictSmg = value;
}

void APBridge::SetVendorSanityEnabled(bool value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_vendorSanityEnabled = value;
}

void APBridge::SetVendorSanityStockLine(const std::string& value)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_vendorSanityStockLine = NormalizeSlotDataRawString(value);
}
} // namespace CyberpunkArchipelago
