module Archipelago

public class APWeaponRestrictionEnforcer extends ScriptableService {
    private let gameState: ref<APGameState>;

    private func OnAttach() -> Void {
        this.gameState = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        APLogger.LogInfo("APWeaponRestrictionEnforcer attached and ready");
    }

    // This function is called by the game's equipment system when checking if a weapon can be equipped
    public func CanEquipWeapon(weaponType: gamedataItemType) -> Bool {
        if !IsDefined(this.gameState) {
            APLogger.LogError("APWeaponRestrictionEnforcer: Game state not defined!");
            return true; // Fail open if we can't access game state
        }


        return true; // If no restrictions are set, allow equipping
    }
}