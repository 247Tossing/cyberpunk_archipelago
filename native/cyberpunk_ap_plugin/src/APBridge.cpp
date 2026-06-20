#include "APBridge.hpp"

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
    AP_RegisterSlotDataIntCallback("restrict_by_major_district", &APBridge::OnSlotDataRestrictByMajorDistrict);
    AP_RegisterSlotDataIntCallback("weapon_restriction_type", &APBridge::OnSlotDataWeaponRestrictionType);
    AP_RegisterSlotDataIntCallback("weapon_restrict_pistol", &APBridge::OnSlotDataWeaponRestrictPistol);
    AP_RegisterSlotDataIntCallback("weapon_restrict_melee", &APBridge::OnSlotDataWeaponRestrictMelee);
    AP_RegisterSlotDataIntCallback("weapon_restrict_rifle", &APBridge::OnSlotDataWeaponRestrictRifle);
    AP_RegisterSlotDataIntCallback("weapon_restrict_sniper", &APBridge::OnSlotDataWeaponRestrictSniper);
    AP_RegisterSlotDataIntCallback("weapon_restrict_lmg", &APBridge::OnSlotDataWeaponRestrictLmg);
    AP_RegisterSlotDataIntCallback("weapon_restrict_shotgun", &APBridge::OnSlotDataWeaponRestrictShotgun);
    AP_RegisterSlotDataIntCallback("weapon_restrict_smg", &APBridge::OnSlotDataWeaponRestrictSmg);

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
    m_restrictByMajorDistrict = false;
    m_weaponRestrictionType = 0;
    m_weaponRestrictPistol = false;
    m_weaponRestrictMelee = false;
    m_weaponRestrictRifle = false;
    m_weaponRestrictSniper = false;
    m_weaponRestrictLmg = false;
    m_weaponRestrictShotgun = false;
    m_weaponRestrictSmg = false;
    std::queue<int64_t> empty;
    m_receivedItemIds.swap(empty);
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
        return false;
    }

    AP_DeathLinkSend(cause);
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
    if (m_receivedItemIds.empty())
    {
        return false;
    }

    outItemId = m_receivedItemIds.front();
    m_receivedItemIds.pop();
    return true;
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

bool APBridge::GetRestrictByMajorDistrict() const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_restrictByMajorDistrict;
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

void APBridge::OnItemClear()
{
    std::lock_guard<std::mutex> lock(APBridge::Get().m_mutex);
    std::queue<int64_t> empty;
    APBridge::Get().m_receivedItemIds.swap(empty);
}

void APBridge::OnItemReceived(int64_t itemId, bool)
{
    APBridge::Get().PushItem(itemId);
}

void APBridge::OnLocationChecked(int64_t)
{
}

void APBridge::OnDeathLinkReceived()
{
    APBridge::Get().MarkDeathLinkPending();
}

void APBridge::OnSlotDataRestrictByMajorDistrict(int value)
{
    APBridge::Get().SetRestrictByMajorDistrict(value != 0);
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

void APBridge::PushItem(int64_t itemId)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_receivedItemIds.push(itemId);
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
} // namespace CyberpunkArchipelago
