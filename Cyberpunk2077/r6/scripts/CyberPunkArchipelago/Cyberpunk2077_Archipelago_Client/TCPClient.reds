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
        AP_SendDeathLink("");
    }

    public func SendReadySignal() -> Void {
    }

    public func SendSyncCheckRequest() -> Void {
    }

    public func SendSyncCompleteResponse(currentCount: Int32) -> Void {
    }

    public func Pump() -> Void {
        // Apply slot config received from the server (e.g. district restriction).
        // The native bridge captures restrict_by_major_district from the Connected
        // packet's slot_data; mirror it into APGameState so enforcement can read it.
        if this.IsConnected() {
            let gameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
            if IsDefined(gameState) {
                gameState.SetRestrictByMajorDistrict(AP_GetRestrictByMajorDistrict());
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
        let nextItemId: Int64 = AP_PollItemQueue();
        if nextItemId >= 0l {
            let itemId: String = APNativeMappings.ResolveItemId(nextItemId);
            if StrLen(itemId) > 0 {
                let gameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
                if IsDefined(gameSystem) {
                    gameSystem.HandleItemReceived(itemId);
                }
            } else {
                APLogger.LogDebug(s"TCPClient: No item mapping for AP item ID \(ToString(nextItemId))");
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
