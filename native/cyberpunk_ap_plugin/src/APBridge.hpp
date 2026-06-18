#pragma once

#include <cstdint>
#include <mutex>
#include <queue>
#include <string>

#include "Archipelago.h"

namespace CyberpunkArchipelago
{
class APBridge
{
public:
    static APBridge& Get();

    bool Initialize(const std::string& serverAddress,
                    const std::string& gameName,
                    const std::string& slotName,
                    const std::string& password);
    bool Connect();
    void Shutdown();

    bool IsReady() const;
    bool IsConnected() const;
    int32_t GetConnectionStatus() const;
    std::string GetLastConnectionError() const;

    bool SendLocationCheck(int64_t locationId);
    bool SendDeathLink(const std::string& cause);
    bool SendSay(const std::string& text);
    bool StoryComplete();

    bool PollReceivedItemId(int64_t& outItemId);
    std::string GetPolledItemNotifySender() const;
    std::string GetPolledItemNotifyDisplayName() const;
    bool IsDeathLinkPending() const;
    void ClearDeathLink();
    bool GetDeathLinkEnabled() const;

    bool GetRestrictByMajorDistrict() const;
    bool GetRestrictBySubDistrict() const;
    int32_t GetDistrictTokenGatedMajorMask() const;
    int32_t GetWeaponRestrictionType() const;
    bool GetWeaponRestrictPistol() const;
    bool GetWeaponRestrictMelee() const;
    bool GetWeaponRestrictRifle() const;
    bool GetWeaponRestrictSniper() const;
    bool GetWeaponRestrictLmg() const;
    bool GetWeaponRestrictShotgun() const;
    bool GetWeaponRestrictSmg() const;
    bool GetVendorSanityEnabled() const;
    std::string GetVendorSanityStockLine() const;

private:
    APBridge() = default;
    APBridge(const APBridge&) = delete;
    APBridge& operator=(const APBridge&) = delete;

    static void OnItemClear();
    static void OnItemReceived(int64_t itemId, std::string senderName, std::string itemDisplayName, bool notify);
    static void OnLocationChecked(int64_t locationId);
    static void OnDeathLinkReceived();
    static void OnSlotDataDeathLink(int value);
    static void OnSlotDataRestrictByMajorDistrict(int value);
    static void OnSlotDataRestrictBySubDistrict(int value);
    static void OnSlotDataDistrictTokenGatedMajorMask(int value);
    static void OnSlotDataWeaponRestrictionType(int value);
    static void OnSlotDataWeaponRestrictPistol(int value);
    static void OnSlotDataWeaponRestrictMelee(int value);
    static void OnSlotDataWeaponRestrictRifle(int value);
    static void OnSlotDataWeaponRestrictSniper(int value);
    static void OnSlotDataWeaponRestrictLmg(int value);
    static void OnSlotDataWeaponRestrictShotgun(int value);
    static void OnSlotDataWeaponRestrictSmg(int value);
    static void OnSlotDataVendorSanity(int value);
    static void OnSlotDataVendorSanityStock(std::string value);

    bool IsReadyLocked() const; // caller must hold m_mutex

    void PushItem(int64_t itemId, const std::string& senderName, const std::string& itemDisplayName, bool shouldNotify);

    struct ReceivedItemEntry
    {
        int64_t itemId;
        std::string senderName;
        std::string itemDisplayName;
        bool shouldNotify;
    };
    void MarkDeathLinkPending();
    void SetDeathLinkEnabled(bool value);
    void SetRestrictByMajorDistrict(bool value);
    void SetRestrictBySubDistrict(bool value);
    void SetDistrictTokenGatedMajorMask(int32_t value);
    void SetWeaponRestrictionType(int32_t value);
    void SetWeaponRestrictPistol(bool value);
    void SetWeaponRestrictMelee(bool value);
    void SetWeaponRestrictRifle(bool value);
    void SetWeaponRestrictSniper(bool value);
    void SetWeaponRestrictLmg(bool value);
    void SetWeaponRestrictShotgun(bool value);
    void SetWeaponRestrictSmg(bool value);
    void SetVendorSanityEnabled(bool value);
    void SetVendorSanityStockLine(const std::string& value);

    mutable std::mutex m_mutex;
    bool m_initialized{false};
    bool m_started{false};
    bool m_deathLinkPending{false};
    bool m_deathLinkEnabled{false};
    bool m_restrictByMajorDistrict{false};
    bool m_restrictBySubDistrict{false};
    int32_t m_districtTokenGatedMajorMask{0};
    int32_t m_weaponRestrictionType{0};
    bool m_weaponRestrictPistol{false};
    bool m_weaponRestrictMelee{false};
    bool m_weaponRestrictRifle{false};
    bool m_weaponRestrictSniper{false};
    bool m_weaponRestrictLmg{false};
    bool m_weaponRestrictShotgun{false};
    bool m_weaponRestrictSmg{false};
    bool m_vendorSanityEnabled{false};
    std::string m_vendorSanityStockLine;
    std::queue<ReceivedItemEntry> m_receivedItems;
    std::string m_lastPolledNotifySender;
    std::string m_lastPolledNotifyDisplayName;
};
} // namespace CyberpunkArchipelago
