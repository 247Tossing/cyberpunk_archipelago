module Archipelago

// Handles all inventory and currency operations
// Separates game integration from business logic
// Uses ScriptableSystem pattern for proper lifecycle management
public class APInventoryHandler extends ScriptableSystem {

    public func OnAttach() -> Void {
        APLogger.LogInfo("APInventoryHandler initialized");
    }

    // Give an item to the player's inventory
    public func GiveInventoryItem(itemId: String, amount: Int32) -> Bool {
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();

        if !IsDefined(player) {
            APLogger.LogWarning("APInventoryHandler: Cannot give item - player not available");
            return false;
        }

        let transactionSystem: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.GetGameInstance());
        if !IsDefined(transactionSystem) {
            APLogger.LogWarning("APInventoryHandler: Cannot give item - transaction system not available");
            return false;
        }

        let tdbid: TweakDBID = TDBID.Create(itemId);
        let invItem: ItemID = ItemID.FromTDBID(tdbid);

        transactionSystem.GiveItem(player, invItem, amount);

        return true;
    }

    // Give eddies (money) to the player
    public func GiveEddies(amount: Int32) -> Bool {
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();

        if !IsDefined(player) {
            APLogger.LogWarning("APInventoryHandler: Cannot give eddies - player not available");
            return false;
        }

        let transactionSystem: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.GetGameInstance());
        if !IsDefined(transactionSystem) {
            APLogger.LogWarning("APInventoryHandler: Cannot give eddies - transaction system not available");
            return false;
        }

        let moneyId: ItemID = ItemID.FromTDBID(t"Items.money");
        transactionSystem.GiveItem(player, moneyId, amount);

        return true;
    }

    // Update persistent fact for item tracking
    public func UpdateItemFact(itemId: String, newValue: Int32) -> Void {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if IsDefined(questSystem) {
            questSystem.SetFact(StringToName(itemId), newValue);
        }
    }

    // Get current item count from facts database
    public func GetItemFactCount(itemId: String) -> Int32 {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if IsDefined(questSystem) {
            return questSystem.GetFact(StringToName(itemId));
        }
        return 0;
    }

    // Increment item count fact
    public func IncrementItemFact(itemId: String, incrementBy: Int32) -> Void {
        let currentCount: Int32 = this.GetItemFactCount(itemId);
        this.UpdateItemFact(itemId, currentCount + incrementBy);
    }
}
