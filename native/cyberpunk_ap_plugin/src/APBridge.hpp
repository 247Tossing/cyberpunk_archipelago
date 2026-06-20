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
    bool StoryComplete();

    bool PollReceivedItemId(int64_t& outItemId);
    bool IsDeathLinkPending() const;
    void ClearDeathLink();

    bool GetRestrictByMajorDistrict() const;
    int32_t GetWeaponRestrictionType() const;
    bool GetWeaponRestrictPistol() const;
    bool GetWeaponRestrictMelee() const;
    bool GetWeaponRestrictRifle() const;
    bool GetWeaponRestrictSniper() const;
    bool GetWeaponRestrictLmg() const;
    bool GetWeaponRestrictShotgun() const;
    bool GetWeaponRestrictSmg() const;

private:
    APBridge() = default;
    APBridge(const APBridge&) = delete;
    APBridge& operator=(const APBridge&) = delete;

    static void OnItemClear();
    static void OnItemReceived(int64_t itemId, bool notify);
    static void OnLocationChecked(int64_t locationId);
    static void OnDeathLinkReceived();
    static void OnSlotDataRestrictByMajorDistrict(int value);
    static void OnSlotDataWeaponRestrictionType(int value);
    static void OnSlotDataWeaponRestrictPistol(int value);
    static void OnSlotDataWeaponRestrictMelee(int value);
    static void OnSlotDataWeaponRestrictRifle(int value);
    static void OnSlotDataWeaponRestrictSniper(int value);
    static void OnSlotDataWeaponRestrictLmg(int value);
    static void OnSlotDataWeaponRestrictShotgun(int value);
    static void OnSlotDataWeaponRestrictSmg(int value);

    bool IsReadyLocked() const; // caller must hold m_mutex

    void PushItem(int64_t itemId);
    void MarkDeathLinkPending();
    void SetRestrictByMajorDistrict(bool value);
    void SetWeaponRestrictionType(int32_t value);
    void SetWeaponRestrictPistol(bool value);
    void SetWeaponRestrictMelee(bool value);
    void SetWeaponRestrictRifle(bool value);
    void SetWeaponRestrictSniper(bool value);
    void SetWeaponRestrictLmg(bool value);
    void SetWeaponRestrictShotgun(bool value);
    void SetWeaponRestrictSmg(bool value);

    mutable std::mutex m_mutex;
    bool m_initialized{false};
    bool m_started{false};
    bool m_deathLinkPending{false};
    bool m_restrictByMajorDistrict{false};
    int32_t m_weaponRestrictionType{0};
    bool m_weaponRestrictPistol{false};
    bool m_weaponRestrictMelee{false};
    bool m_weaponRestrictRifle{false};
    bool m_weaponRestrictSniper{false};
    bool m_weaponRestrictLmg{false};
    bool m_weaponRestrictShotgun{false};
    bool m_weaponRestrictSmg{false};
    std::queue<int64_t> m_receivedItemIds;
};
} // namespace CyberpunkArchipelago
