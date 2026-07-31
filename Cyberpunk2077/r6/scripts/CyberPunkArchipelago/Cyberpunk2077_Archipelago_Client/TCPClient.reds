module Archipelago

public class TCPClient extends ScriptableService {
    private let serverAddress: String = "127.0.0.1:38281";
    private let gameName: String = "Cyberpunk 2077";
    private let slotName: String = "Player1";
    private let password: String = "";
    private let initialized: Bool = false;
    private let lastConnectionError: String = "";
    // Tracks APGameSystem availability across Pump ticks so we can log only on transitions
    // (Pump runs ~20x/sec, so logging every tick would flood scripting.log).
    private let lastGameSystemAvailableLogged: Bool = false;
    private let hasLoggedGameSystemAvailability: Bool = false;

    // Settle-tracking for APGameState.itemResyncPending (see ArmItemResyncPending). Counts Pump
    // ticks since pending was armed, and consecutive ticks with no item queue activity, so we know
    // when the post-spawn/connect backlog has finished draining and district enforcement can resume.
    private let ticksSincePendingSet: Int32 = 0;
    private let emptyPollStreakWhilePending: Int32 = 0;

    public func Configure(server: String, game: String, slot: String, pass: String) -> Void {
        this.serverAddress = server;
        this.gameName = game;
        this.slotName = slot;
        this.password = pass;
        this.initialized = AP_Initialize(this.serverAddress, this.gameName, this.slotName, this.password);
        if !this.initialized {
            this.lastConnectionError = AP_GetLastConnectionError();
            if StrLen(this.lastConnectionError) == 0 {
                this.lastConnectionError = "Failed to initialize Archipelago client.";
            }
        }
    }

    public func ConnectFromCET(ip: String, port: Int32, slotName: String) -> Void {
        // Always reset prior connection state so APBridge.Initialize doesn't early-return
        // on reconnect attempts (drops, refusals, or timeouts leave the native layer
        // initialized+started, which would otherwise make Initialize/Connect no-ops).
        AP_Disconnect();
        this.initialized = false;
        this.lastConnectionError = "";

        if port < 0 || port > 65535 {
            this.lastConnectionError = "Invalid port number. Must be between 0 and 65535.";
            APLogger.LogInfo(s"TCPClient: ERROR - \(this.lastConnectionError)");
            return;
        }

        if StrLen(slotName) == 0 {
            this.lastConnectionError = "Slot name cannot be empty.";
            APLogger.LogInfo(s"TCPClient: ERROR - \(this.lastConnectionError)");
            return;
        }

        this.Configure(s"\(ip):\(port)", this.gameName, slotName, this.password);
        if !this.initialized {
            APLogger.LogInfo(s"TCPClient: ERROR - \(this.lastConnectionError)");
            return;
        }

        if !AP_Connect() {
            this.lastConnectionError = AP_GetLastConnectionError();
            if StrLen(this.lastConnectionError) == 0 {
                this.lastConnectionError = "Failed to start Archipelago connection.";
            }
            APLogger.LogInfo(s"TCPClient: ERROR - \(this.lastConnectionError)");
        }
    }

    public func DisconnectFromCET() -> Void {
        AP_Disconnect();
        this.initialized = false;
        this.lastConnectionError = "";
    }

    public func IsConnected() -> Bool {
        return AP_IsConnected();
    }

    public func GetConnectionStatusCode() -> Int32 {
        return AP_GetConnectionStatus();
    }

    public func GetLastConnectionError() -> String {
        let nativeError: String = AP_GetLastConnectionError();
        if StrLen(nativeError) > 0 {
            this.lastConnectionError = nativeError;
        }
        return this.lastConnectionError;
    }

    public func GetConnectionStatusMessage() -> String {
        let status: Int32 = AP_GetConnectionStatus();
        if status == 2 {
            return "Connected to Archipelago";
        }
        if status == 1 {
            return "Connected (auth pending)";
        }
        if status == 4 {
            return "Negotiating with server...";
        }
        if status == 3 {
            let errorMessage: String = this.GetLastConnectionError();
            if StrLen(errorMessage) > 0 {
                return s"Connection refused: \(errorMessage)";
            }
            return "Connection refused";
        }
        if this.initialized {
            return "Connecting...";
        }
        return "Not connected";
    }

    public func SendCheck(checkString: String) -> Void {
        if !this.IsConnected() {
            APLogger.LogInfo(s"TCPClient: Not connected, dropping check: \(checkString)");
            return;
        }

        let locationAddress: Int64 = APNativeMappings.ResolveLocationAddress(checkString);
        if locationAddress < 0l {
            APLogger.LogInfo(s"TCPClient: No location mapping for \(checkString)");
            return;
        }

        let sent: Bool = AP_SendLocationCheck(locationAddress);
        if !sent {
            APLogger.LogInfo(s"TCPClient: AP_SendLocationCheck failed for \(checkString)");
        }
    }

    public func SendDeathLink() -> Void {
        AP_SendDeathLink("");
    }

    public func SendReadySignal() -> Void {
    }

    public func SendSyncCheckRequest() -> Void {
    }

    public func SendSyncCompleteResponse(currentCount: Int32) -> Void {
    }

    // Marks a district-enforcement deferral window: APDistrictManager.HandleDistrictRestriction will
    // not teleport the player while APGameState.itemResyncPending is set, since quest facts read
    // during this window may not yet reflect tokens the player already owns (the native item queue
    // is still being drained by Pump after a save load or fresh connect). Resets the settle counters
    // so Pump starts watching for the queue to go quiet again.
    private func ArmItemResyncPending() -> Void {
        let gameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if !IsDefined(gameState) {
            return;
        }
        if !gameState.IsItemResyncPending() {
            APLogger.LogDebug("TCPClient: Arming item resync pending - deferring district enforcement until item queue settles");
        }
        gameState.SetItemResyncPending(true);
        this.ticksSincePendingSet = 0;
        this.emptyPollStreakWhilePending = 0;
    }

    // Called once per spawn (from APGameSystem's OnMakePlayerVisibleAfterSpawn hook) so enforcement
    // is deferred as soon as possible after a save load, before any DistrictEnteredEvent can fire.
    public func OnPlayerSpawned() -> Void {
        if this.IsConnected() {
            this.ArmItemResyncPending();
        }
    }

    public func Pump() -> Void {
        // Fetched once up front and reused for both the slot-config mirroring below and the
        // item-resync-pending settle tracking at the end of this function.
        let gameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;

        // Apply slot config received from the server (e.g. district restriction).
        // The native bridge captures restrict_by_major_district from the Connected
        // packet's slot_data; mirror it into APGameState so enforcement can read it.
        if this.IsConnected() {
            if IsDefined(gameState) {
                let districtRestrictionChanged: Bool = gameState.SetRestrictByMajorDistrict(AP_GetRestrictByMajorDistrict());
                if districtRestrictionChanged {
                    APLogger.LogInfo(s"District restriction config received: restrictByMajorDistrict=\(gameState.restrictByMajorDistrict)");
                }
                let weaponConfigChanged: Bool = gameState.SetWeaponRestrictionConfig(
                    AP_GetWeaponRestrictionType(),
                    AP_GetWeaponRestrictPistol(),
                    AP_GetWeaponRestrictMelee(),
                    AP_GetWeaponRestrictRifle(),
                    AP_GetWeaponRestrictSniper(),
                    AP_GetWeaponRestrictLmg(),
                    AP_GetWeaponRestrictShotgun(),
                    AP_GetWeaponRestrictSmg()
                );
                if weaponConfigChanged {
                    APLogger.LogInfo(
                        s"Weapon restriction config received: type=\(ToString(gameState.weaponRestrictionType)), pistol=\(gameState.weaponRestrictPistol), melee=\(gameState.weaponRestrictMelee), rifle=\(gameState.weaponRestrictRifle), sniper=\(gameState.weaponRestrictSniper), lmg=\(gameState.weaponRestrictLmg), shotgun=\(gameState.weaponRestrictShotgun), smg=\(gameState.weaponRestrictSmg)"
                    );
                }
            }
        }

        // Poll item queue from APCpp.
        // Item ID -> in-game mapping is handled in RedScript via APNativeMappings.ResolveItemId.
        //
        // Only poll while APGameSystem is available (i.e. a save is loaded). Polling from the main
        // menu or before the world is ready would pop the item off the native queue with nowhere to
        // apply it, permanently losing it even though the server considers it delivered. Leaving it
        // queued here means it's applied as soon as a save is loaded and Pump runs again.
        let gameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
        let gameSystemAvailable: Bool = IsDefined(gameSystem);
        // Bool has no != overload in RedScript - use the same XOR-style comparison as
        // APGameState.SetRestrictByMajorDistrict / SetWeaponRestrictionConfig.
        let gameSystemAvailabilityChanged: Bool = (gameSystemAvailable && !this.lastGameSystemAvailableLogged) || (!gameSystemAvailable && this.lastGameSystemAvailableLogged);
        if !this.hasLoggedGameSystemAvailability || gameSystemAvailabilityChanged {
            APLogger.LogDebug(s"TCPClient.Pump: APGameSystem availability changed -> \(gameSystemAvailable)");
            if !gameSystemAvailable {
                APLogger.LogDebug("TCPClient.Pump: item queue will not be polled/drained until a save is loaded");
            } else if this.IsConnected() {
                // The system can become available without a fresh spawn callback (e.g. it attaches
                // right as Pump runs). Defer enforcement here too, same as OnPlayerSpawned.
                APLogger.LogDebug("TCPClient.Pump: APGameSystem became available while connected - deferring district enforcement until item queue settles");
                this.ArmItemResyncPending();
            }
            this.lastGameSystemAvailableLogged = gameSystemAvailable;
            this.hasLoggedGameSystemAvailability = true;
        }

        let itemAppliedThisTick: Bool = false;
        if IsDefined(gameSystem) {
            let nextItemId: Int64 = AP_PollItemQueue();
            if nextItemId >= 0l {
                let itemId: String = APNativeMappings.ResolveItemId(nextItemId);
                if StrLen(itemId) > 0 {
                    itemAppliedThisTick = true;
                    let networkIndex: Int32 = AP_GetPolledItemNetworkIndex();
                    let inventoryHandler: ref<APInventoryHandler> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APInventoryHandler") as APInventoryHandler;
                    let shouldGrant: Bool = true;
                    let lastProcessedIndexForLog: Int32 = -1;
                    if IsDefined(inventoryHandler) {
                        lastProcessedIndexForLog = inventoryHandler.GetLastNetworkItemIndex();
                    }
                    APLogger.LogDebug(
                        s"TCPClient.Pump: polled AP item id=\(ToString(nextItemId)) resolvedItemId='\(itemId)' networkIndex=\(networkIndex) lastProcessedIndex=\(lastProcessedIndexForLog)"
                    );

                    // If this item's network index is older than the last one we already applied
                    // live, the server is resending something we've already processed (typically on
                    // reconnect). Route it through the sync path instead of granting it again, so
                    // one-shot effects (traps) don't replay and inventory/eddies aren't duplicated -
                    // while still letting durable state (quest keys, district tokens) reconcile.
                    if networkIndex >= 0 && IsDefined(inventoryHandler) {
                        let lastProcessedIndex: Int32 = inventoryHandler.GetLastNetworkItemIndex();
                        if networkIndex < lastProcessedIndex {
                            shouldGrant = false;
                            APLogger.LogDebug(s"TCPClient.Pump: '\(itemId)' networkIndex(\(networkIndex)) < lastProcessedIndex(\(lastProcessedIndex)) - routing through HandleItemSync (resync)");
                            if IsDefined(gameState) {
                                gameSystem.HandleItemSync(itemId, gameState);
                            }
                        }
                    }

                    if shouldGrant {
                        APLogger.LogDebug(s"TCPClient.Pump: '\(itemId)' routing through HandleItemReceived (live grant)");
                        gameSystem.HandleItemReceived(itemId);
                        if networkIndex >= 0 && IsDefined(inventoryHandler) {
                            inventoryHandler.SetLastNetworkItemIndex(networkIndex + 1);
                        }
                    }
                } else {
                    APLogger.LogDebug(s"TCPClient: No item mapping for AP item ID \(ToString(nextItemId))");
                }
            }
        }

        // Settle tracking for APGameState.itemResyncPending (see ArmItemResyncPending). Once the
        // item queue has gone quiet for a bit (or a hard timeout elapses as a safety net), re-run
        // SyncData once more to catch anything the backlog just delivered, then let district
        // enforcement resume.
        if IsDefined(gameState) && gameState.IsItemResyncPending() {
            this.ticksSincePendingSet += 1;
            if itemAppliedThisTick {
                this.emptyPollStreakWhilePending = 0;
            } else {
                this.emptyPollStreakWhilePending += 1;
            }

            let emptyPollSettleThreshold: Int32 = 40; // ~2s of no new items at ~20 Pump ticks/sec
            let pendingHardTimeoutTicks: Int32 = 600; // ~30s safety net so enforcement can't stay off forever
            if this.emptyPollStreakWhilePending >= emptyPollSettleThreshold || this.ticksSincePendingSet >= pendingHardTimeoutTicks {
                APLogger.LogInfo(
                    s"TCPClient.Pump: item queue settled (emptyPollStreak=\(this.emptyPollStreakWhilePending), ticksSincePending=\(this.ticksSincePendingSet)) - resuming district enforcement"
                );
                gameState.SetItemResyncPending(false);
                this.ticksSincePendingSet = 0;
                this.emptyPollStreakWhilePending = 0;
                if IsDefined(gameSystem) {
                    gameSystem.SyncData();
                }
            }
        }

        if AP_IsDeathLinkPending() {
            let gameSystemDL: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
            if IsDefined(gameSystemDL) {
                gameSystemDL.HandleDeathLink();
            }
            AP_ClearDeathLink();
        }
    }
}
