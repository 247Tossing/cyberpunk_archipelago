module Archipelago

public class APWeaponRestrictionEnforcer extends ScriptableService {

    private func OnAttach() -> Void {
        APLogger.LogInfo("APWeaponRestrictionEnforcer attached and ready");
    }

    // This function is called by the game's equipment system when checking if a weapon can be equipped
    // weaponRestrictionType: 0 = none, 1 = cannotEquip (hard ban), 2 = requireMultiworldItem (pass-gated)
    public func CanEquipWeapon(weaponType: gamedataItemType) -> Bool {
        let gameState = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if !IsDefined(gameState) {
            APLogger.LogError("APWeaponRestrictionEnforcer: Game state not defined!");
            return true; // Fail open if we can't access game state
        }

        // Mode 0: No restrictions at all — allow everything
        if (gameState.weaponRestrictionType == 0) {
            return true;
        }

        // Check if this specific weapon type is restricted by the player's options
        if !this.IsWeaponTypeRestricted(weaponType, gameState) {
            return true; // This weapon type is not restricted, allow equipping
        }

        // Mode 1: Cannot Equip — hard ban restricted weapon types, no way to unlock
        if (gameState.weaponRestrictionType == 1) {
            return false;
        }

        // Mode 2: Require Multiworld Item — check if the player has the pass
        if (gameState.weaponRestrictionType == 2) {
            APLogger.LogDebug(s"Weapon Type is \(weaponType)");
            let requiredPass = APConstants.GetRequiredWeaponPassStr(weaponType);
            // Empty string means unmapped type (vehicle weapons, etc.) — allow
            if Equals(requiredPass, "") {
                return true;
            }
            let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(GetGameInstance()) as QuestsSystem;
            if !IsDefined(questSystem) {
                APLogger.LogError("APWeaponRestrictionEnforcer: Quest system not defined!");
                return true; // Fail open if we can't access quest system
            }
            APLogger.LogDebug(s"Checking for required pass: \(requiredPass)");
            if (questSystem.GetFact(StringToName(requiredPass)) > 0) {
                APLogger.LogDebug("Player has the required pass");
                return true; // Player has the required pass
            }
            return false; // Player does not have the required pass
        }

        // Unknown mode — fail open
        return true;
    }

    // Check if a weapon type is restricted based on the individual per-type flags
    private func IsWeaponTypeRestricted(weaponType: gamedataItemType, gameState: ref<APGameState>) -> Bool {
        if APConstants.IsPistol(weaponType)  { return gameState.weaponRestrictPistol; }
        if APConstants.IsRifle(weaponType)   { return gameState.weaponRestrictRifle; }
        if APConstants.IsShotgun(weaponType) { return gameState.weaponRestrictShotgun; }
        if APConstants.IsSniper(weaponType)  { return gameState.weaponRestrictSniper; }
        if APConstants.IsSMG(weaponType)     { return gameState.weaponRestrictSmg; }
        if APConstants.IsLMG(weaponType)     { return gameState.weaponRestrictLmg; }
        if APConstants.IsMelee(weaponType)   { return gameState.weaponRestrictMelee; }
        // Unmapped types (vehicle weapons, grenade launchers, cyberware, etc.) are never restricted
        return false;
    }
}

@wrapMethod(InventoryDataManagerV2)
public final func EquipItem(itemId: ItemID, slot: Int32) -> Void {
    APLogger.LogDebug(s"Incoming Item equip attempt");
    let weaponEnforcer = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APWeaponRestrictionEnforcer") as APWeaponRestrictionEnforcer;
    if IsDefined(weaponEnforcer) {
        let incomingItem = itemId.GetTDBID();
        let itemRecord: ref<Item_Record> = TweakDBInterface.GetItemRecord(incomingItem);
        let itemType = itemRecord.ItemType().Type();
        APLogger.LogDebug(s"Item Type is: \(itemType)");
        if weaponEnforcer.CanEquipWeapon(itemType) {
                APLogger.LogDebug("Weapon equip allowed");
                wrappedMethod(itemId, slot); // Proceed with the equip action
            } else {
                APLogger.LogDebug("Weapon equip blocked by Archipelago restrictions");
                return; // Block the equip action
        }
    }
}