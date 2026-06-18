module Archipelago

public class TCPClient extends ScriptableService {
    private let serverAddress: String = "127.0.0.1:38281";
    private let gameName: String = "Cyberpunk 2077";
    private let slotName: String = "Player1";
    private let password: String = "";
    private let initialized: Bool = false;
    private let lastConnectionError: String = "";

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
        let message: String = s"\(this.slotName) died in Night City";
        if !this.IsConnected() {
            APLogger.LogInfo("DeathLink: SendDeathLink aborted — not connected to Archipelago");
            return;
        }
        let said: Bool = AP_Say(message);
        if said {
            APLogger.LogInfo("DeathLink: announced death in chat");
        } else {
            APLogger.LogInfo("DeathLink: chat announce failed — not connected");
        }

        APLogger.LogDebug(s"DeathLink: SendDeathLink calling native — cause=\"\(message)\", slot=\"\(this.slotName)\"");
        let sent: Bool = AP_SendDeathLink(message);
        if sent {
            APLogger.LogInfo(s"DeathLink: AP_SendDeathLink returned true (cause=\"\(message)\")");
        } else {
            APLogger.LogInfo("DeathLink: AP_SendDeathLink returned false — native bridge not ready");
        }
    }

    public func SendReadySignal() -> Void {
    }

    public func SendSyncCheckRequest() -> Void {
    }

    public func SendSyncCompleteResponse(currentCount: Int32) -> Void {
    }

    public func Pump() -> Void {
        // Apply slot config received from the server (e.g. district restriction).
        // The native bridge captures these from the Connected packet's slot_data;
        // mirror them into APGameState so enforcement can read them.
        if this.IsConnected() {
            let gameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
            if IsDefined(gameState) {
                let changed: Bool = gameState.SetDistrictRestrictionConfig(
                    AP_GetRestrictByMajorDistrict(),
                    AP_GetRestrictBySubDistrict(),
                    AP_GetDistrictTokenGatedMajorMask()
                );
                if changed {
                    let gatedSummary: String = gameState.GetGatedDistrictSummary();
                    let autoOpenSummary: String = gameState.GetAutoOpenDistrictSummary();
                    APLogger.LogInfo(
                        s"District restriction config received: major=\(gameState.restrictByMajorDistrict), sub=\(gameState.restrictBySubDistrict), gated=\(gatedSummary), auto_open=\(autoOpenSummary)"
                    );

                    let districtGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
                    if IsDefined(districtGameSystem) {
                        districtGameSystem.ApplyDistrictRestrictionConfig();
                    }
                }

                let vendorChanged: Bool = gameState.SetVendorSanityData(
                    AP_GetVendorSanityEnabled(),
                    AP_GetVendorSanityStockLine()
                );
                if vendorChanged {
                    APLogger.LogInfo(
                        s"Vendor sanity data received: enabled=\(gameState.vendorSanityEnabled), slots=\(ToString(ArraySize(gameState.vendorSanityItems)))"
                    );
                }

                let nativeDeathLinkEnabled: Bool = AP_GetDeathLinkEnabled();
                let deathLinkChanged: Bool = gameState.SetEnableDeathLink(nativeDeathLinkEnabled);
                if deathLinkChanged {
                    APLogger.LogInfo(s"DeathLink: config synced from slot_data — enabled=\(gameState.enableDeathLink)");
                }
            }
        }

        // Poll item queue from APCpp.
        // Item ID -> in-game mapping is handled in RedScript via APNativeMappings.ResolveItemId.
        let nextItemId: Int64 = AP_PollItemQueue();
        if nextItemId >= 0l {
            let itemId: String = APNativeMappings.ResolveItemId(nextItemId);
            if StrLen(itemId) > 0 {
                let gameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
                if IsDefined(gameSystem) {
                    gameSystem.HandleItemReceived(itemId);
                    let senderName: String = AP_GetPolledItemNotifySender();
                    if StrLen(senderName) == 0 {
                        senderName = "Archipelago";
                    }
                    let itemDisplayName: String = AP_GetPolledItemNotifyDisplayName();
                    if StrLen(itemDisplayName) == 0 {
                        itemDisplayName = itemId;
                    }
                    APLogger.LogDebug(s"TCPClient: Dispatching item notification - sender: \(senderName), item: \(itemDisplayName)");
                    gameSystem.HandleItemReceivedNotification(senderName, itemDisplayName);
                }
            } else {
                APLogger.LogDebug(s"TCPClient: No item mapping for AP item ID \(ToString(nextItemId))");
            }
        }

        if AP_IsDeathLinkPending() {
            APLogger.LogDebug("DeathLink: inbound pending — attempting HandleDeathLink");
            let gameSystemDL: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
            if !IsDefined(gameSystemDL) {
                APLogger.LogDebug("DeathLink: inbound deferred — APGameSystem undefined");
            } else if gameSystemDL.HandleDeathLink() {
                APLogger.LogInfo("DeathLink: inbound applied — clearing pending flag");
                AP_ClearDeathLink();
            } else {
                APLogger.LogDebug("DeathLink: inbound deferred — player or APGameState not ready");
            }
        }
    }
}
