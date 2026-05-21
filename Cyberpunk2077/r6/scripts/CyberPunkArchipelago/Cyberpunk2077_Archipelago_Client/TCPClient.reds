// TCPClient.reds
// Archipelago client service – now backed by the APNativeClient native class
// (CyberpunkArchipelagoPlugin.dll via Red4EXT) instead of a Python bridge.
//
// The public API of this ScriptableService is intentionally kept identical to
// the previous RedSocket-based version so that APGameSystem.reds and the CET
// init.lua do not need to change their call sites.

module Archipelago

public class TCPClient extends ScriptableService {

    private let m_client: ref<APNativeClient>;

    // -----------------------------------------------------------------------
    // Lifecycle
    // -----------------------------------------------------------------------

    private func OnInitialize() -> Void {
        this.m_client = new APNativeClient();
    }

    // -----------------------------------------------------------------------
    // Connection (called from CET init.lua)
    // -----------------------------------------------------------------------

    /// @param ip       Archipelago server hostname or IP
    /// @param port     Archipelago server port (default 38281, NOT 51234)
    /// @param slotName Player slot name
    public func ConnectFromCET(ip: String, port: Int32, slotName: String) -> Void {
        this.ConnectFromCETWithPassword(ip, port, slotName, "");
    }

    /// Extended variant that also accepts a room password.
    public func ConnectFromCETWithPassword(ip: String, port: Int32,
                                           slotName: String, password: String) -> Void {
        if port < 1 || port > 65535 {
            APLogger.LogError("TCPClient: Invalid port number.");
            return;
        }
        if !IsDefined(this.m_client) {
            this.m_client = new APNativeClient();
        }
        APLogger.LogInfo(s"TCPClient: Connecting to \(ip):\(port) as \(slotName)");
        this.m_client.Connect(ip, port, slotName, password);
    }

    public func DisconnectFromCET() -> Void {
        if IsDefined(this.m_client) {
            this.m_client.Disconnect();
        }
    }

    public func IsConnected() -> Bool {
        return IsDefined(this.m_client) && this.m_client.IsConnected();
    }

    public func GetConnectionStatusMessage() -> String {
        if IsDefined(this.m_client) {
            return this.m_client.GetConnectionStatus();
        }
        return "Not connected";
    }

    // -----------------------------------------------------------------------
    // Outgoing events (same surface as the old TCP version)
    // -----------------------------------------------------------------------

    public func SendCheck(checkString: String) -> Void {
        if IsDefined(this.m_client) && this.m_client.IsConnected() {
            this.m_client.SendCheck(checkString);
        } else {
            APLogger.LogInfo("TCPClient: Cannot send check – not connected.");
        }
    }

    public func SendTarotCheck(tarotNumber: Int32) -> Void {
        if IsDefined(this.m_client) && this.m_client.IsConnected() {
            this.m_client.SendTarotCheck(tarotNumber);
        }
    }

    public func SendDeathLink() -> Void {
        if IsDefined(this.m_client) && this.m_client.IsConnected() {
            this.m_client.SendDeathLink("Cyberpunk2077");
        } else {
            APLogger.LogInfo("TCPClient: Cannot send DeathLink – not connected.");
        }
    }

    public func SendStoryComplete() -> Void {
        if IsDefined(this.m_client) && this.m_client.IsConnected() {
            this.m_client.StoryComplete();
        }
    }

    // Kept for backward compatibility – the old code called these after the
    // Python handshake to kick off item/check sync.  With APCpp the sync
    // happens automatically via callbacks; these are now no-ops.
    public func SendSyncCheckRequest() -> Void {}
    public func SendReadySignal() -> Void {}
    public func SendSyncCompleteResponse(currentCount: Int32) -> Void {}

    // -----------------------------------------------------------------------
    // Polling – call on player spawn (and optionally on a tick)
    // -----------------------------------------------------------------------

    /// Process all pending signals from the native client.
    /// Call this on player spawn and whenever you want to deliver queued items.
    ///
    /// Handles:
    ///   • IsClearRequested  → wipes APGameState items so they can be re-applied
    ///   • HasPendingItems   → delivers each queued item to APGameSystem
    ///   • IsDeathLinkPending → kills the player
    ///   • Slot-data config  → applies weapon/district/deathlink config
    public func Poll() -> Void {
        if !IsDefined(this.m_client) || !this.m_client.IsConnected() {
            return;
        }

        let gameSystem: ref<APGameSystem> =
            GetGameInstance().GetScriptableSystemsContainer()
                .Get(n"Archipelago.APGameSystem") as APGameSystem;
        let gameState: ref<APGameState> =
            GameInstance.GetScriptableServiceContainer()
                .GetService(n"Archipelago.APGameState") as APGameState;

        if !IsDefined(gameSystem) || !IsDefined(gameState) {
            return;
        }

        // 1. Full re-sync requested (initial connect / reconnect)
        if this.m_client.IsClearRequested() {
            this.m_client.ConsumeClearRequest();
            gameState.items = new APItemList();
            gameState.totalNetworkItemsReceived = 0;
            APLogger.LogInfo("TCPClient: Item state cleared for re-sync.");
        }

        // 2. Apply slot-data config (idempotent – safe to call every poll)
        this.ApplySlotData(gameState);

        // 3. Deliver queued items
        while this.m_client.HasPendingItems() {
            let itemGameId: String      = this.m_client.PollNextItem();
            let senderName: String      = this.m_client.PollNextItemSender();
            let displayName: String     = this.m_client.PollNextItemDisplayName();
            this.m_client.ClearPendingItem();

            if StrLen(itemGameId) == 0 { continue; }

            APLogger.LogDebug(s"TCPClient: Received \(displayName) from \(senderName)");
            gameSystem.HandleItemReceived(itemGameId);
            gameSystem.HandleItemReceivedNotification(senderName, displayName);
        }

        // 4. DeathLink
        if this.m_client.IsDeathLinkPending() {
            this.m_client.ClearDeathLink();
            gameSystem.HandleDeathLink();
        }
    }

    // -----------------------------------------------------------------------
    // Private helpers
    // -----------------------------------------------------------------------

    private func ApplySlotData(gameState: ref<APGameState>) -> Void {
        gameState.enableDeathLink =
            this.m_client.GetSlotDataBool("death_link", false);

        gameState.skillPointsAsItems =
            this.m_client.GetSlotDataBool("skill_points_as_items", false);

        gameState.restrictByMajorDistrict =
            this.m_client.GetSlotDataBool("restrict_by_major_district", false);

        gameState.weaponRestrictionType =
            this.m_client.GetSlotDataInt("weapon_restriction_type", 0);

        gameState.weaponRestrictPistol  =
            this.m_client.GetSlotDataBool("weapon_restrict_pistol",  false);
        gameState.weaponRestrictSmg     =
            this.m_client.GetSlotDataBool("weapon_restrict_smg",     false);
        gameState.weaponRestrictShotgun =
            this.m_client.GetSlotDataBool("weapon_restrict_shotgun", false);
        gameState.weaponRestrictSniper  =
            this.m_client.GetSlotDataBool("weapon_restrict_sniper",  false);
        gameState.weaponRestrictLmg     =
            this.m_client.GetSlotDataBool("weapon_restrict_lmg",     false);
        gameState.weaponRestrictRifle   =
            this.m_client.GetSlotDataBool("weapon_restrict_rifle",   false);
        gameState.weaponRestrictMelee   =
            this.m_client.GetSlotDataBool("weapon_restrict_melee",   false);
    }
}
