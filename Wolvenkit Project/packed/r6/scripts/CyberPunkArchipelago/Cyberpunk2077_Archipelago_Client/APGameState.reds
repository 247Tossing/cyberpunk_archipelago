module Archipelago

// Pure data holder for Archipelago game state
// All business logic has been moved to APGameSystem
public class APGameState extends ScriptableService {
    // State flags
    public let diedFromDeathLink: Bool;
    public let skillPointsAsItems: Bool;
    public let enableDeathLink: Bool;

    // Item tracking
    public let items: ref<APItemList>;

    // Track total NetworkItems received from Python (not unique item types)
    // This matches Python's len(received_items) counting for SYNC_COMPLETE
    public let totalNetworkItemsReceived: Int32;

    private func OnAttach() -> Void {
        this.items = new APItemList();
        APLogger.LogInfo("Cyberpunk 2077 Archipelago Game State Ready");
    }

    // ===== SIMPLE GETTERS/SETTERS ONLY =====

    public func GetItems() -> ref<APItemList> {
        return this.items;
    }

    public func DiedFromDeathLink() -> Void {
        this.diedFromDeathLink = true;
    }

    public func HandlePlayerRespawn() -> Void {
        this.diedFromDeathLink = false;
    }
}
