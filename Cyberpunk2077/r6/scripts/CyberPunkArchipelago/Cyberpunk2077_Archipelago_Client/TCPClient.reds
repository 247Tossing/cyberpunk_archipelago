module Archipelago
import RedSocket.*

public class TCPClient extends ScriptableService {  
    private let socketService: ref<APRedSocketTCPService>;

    public func SendSyncCheckRequest() -> Void {
        if IsDefined(this.socketService){
            this.socketService.SendSyncCheckRequest();
        }
    }

    public func SendDeathLink() -> Void {

        if IsDefined(this.socketService) && this.socketService.isConnected {
            //APLogger.LogInfo( "TCPClient: Sending DeathLink message to server.");
            let payload: String = "DEATHLINK_SEND";
            this.socketService.SendMessage(payload);
        } else {
            APLogger.LogInfo( "TCPClient: ERROR - Cannot send DeathLink, socket is closed!");
        }
    }

    public func SendCheck(checkString: String) -> Void {
        if IsDefined(this.socketService) && this.socketService.isConnected {
            //APLogger.LogInfo( "TCPClient: Sending Check message to server: " + checkString);
            let payload: String = s"CHECK:\(checkString)";
            this.socketService.SendMessage(payload);
        } else {
            APLogger.LogInfo( "TCPClient: ERROR - Cannot send Check, socket is closed!");
        }
    }

    public func ConnectFromCET(ip: String, port: Int32, slotName: String) -> Void {
        //APLogger.LogInfo( s"TCPClient: ConnectFromCET called with IP: \(ip), Port: \(port), SlotName: \(slotName)");

        if port < 0 || port > 65535 {
            APLogger.LogInfo( "TCPClient: ERROR - Invalid port number. Must be between 0 and 65535.");
            return;
        }

        this.AttemptConnectionToAPServer(ip, Cast<Uint16>(port), slotName);
    }

    public func SendSyncCompleteResponse(currentCount: Int32) -> Void {
        //APLogger.LogInfo( s"TCPClient: Sending SYNC_COMPLETE with count \(currentCount)");
        this.socketService.SendMessage(s"SYNC_COMPLETE:CURRENT_COUNT:\(currentCount)\r\n");
    }

    public func SendReadySignal() -> Void {
        if IsDefined(this.socketService) && this.socketService.isConnected {
            //APLogger.LogInfo( "TCPClient: Sending Ready Signal to server.");
            let payload: String = "OK_READY";
            this.socketService.SendMessage(payload);
        } else {
            APLogger.LogInfo( "TCPClient: ERROR - Cannot send Ready Signal, socket is closed!");
        }
    }

    private func AttemptConnectionToAPServer(ip: String, port: Uint16, slotName: String) -> Void {
        if !IsDefined(this.socketService) {
            this.socketService = new APRedSocketTCPService();
            this.socketService.Initialize(ip, port, slotName);
            this.socketService.Connect();
        }
        if IsDefined(this.socketService) && !this.socketService.isConnected {
            this.socketService.Initialize(ip, port, slotName);
            this.socketService.Connect();
        }
        else {
            //APLogger.LogInfo( "TCPClient: Socket service already initialized. Ignoring duplicate connection attempt.");
        }
    }

    public func DisconnectFromCET() -> Void {
        if IsDefined(this.socketService) {
            this.socketService.Disconnect();
            this.socketService = null;
        }
    }

    public func IsConnected() -> Bool {
        if IsDefined(this.socketService) {
            return this.socketService.isConnected;
        }
        return false;
    }

    public func GetConnectionStatusMessage() -> String {
        if IsDefined(this.socketService) {
            if this.socketService.isConnected {
                return "Connected to Python bridge";
            }
        }
        return "Not connected";
    }
}

public class APRedSocketTCPService extends IScriptable {
    private let socket: ref<Socket>; 

    private let ip: String = "";
    private let port: Uint16;
    public let isConnected: Bool = false;
    private let slotName: String = "";
    private let APClientVersion: String = "0.1.0";
    private let CyberpunkTCPServerRequiredVersion: String = "0.1.0";


    public final func Initialize(targetIp: String, targetPort: Uint16, slotName: String) -> Void {
        this.ip = targetIp;
        this.port = targetPort;
        this.slotName = slotName;

        this.socket = Socket.Create(); //Create a new Socket instance
        
        //APLogger.LogInfo( s"TCPClient: Configured for \(this.ip):\(this.port)");
    }

    // 2. Open the connection
    public final func Connect() -> Void {
        if IsDefined(this.socket) && !this.isConnected {
            APLogger.LogInfo( "Attempting Connection To:" + this.ip + ":" + ToString(this.port));
            
            this.socket.RegisterListener(this, n"OnCommand", n"OnConnected", n"OnDisconnected");

            // Call RedSocket's native connect method
            this.socket.Connect(this.ip, this.port);
            this.isConnected = true;
        }
    }

    // 3. Send a JSON payload to the AP Server
    public final func SendMessage(payload: String) -> Void {
        if IsDefined(this.socket) && this.isConnected {
            //APLogger.LogInfo( "TCPClient: Sending message to server: " + payload);
            this.socket.SendCommand(payload);
        } else {
            APLogger.LogInfo( "TCPClient: ERROR - Cannot send message, socket is closed!");
        }
    }

    // 4. Safely close the connection (Crucial for when the player quits to desktop)
    public final func Disconnect() -> Void {
        if IsDefined(this.socket) && this.isConnected {
            APLogger.LogInfo( "Closing connection.");
            this.socket.Disconnect();
            this.isConnected = false;
        }
    }

    public cb func OnConnected(status: Int32) -> Void {
        //APLogger.LogInfo( "TCPClient: Status recieved");
        if status == 0 {
            APLogger.LogInfo( "Successfully connected to Cyberpunk AP Client Server.");
            this.isConnected = true;
            this.SendHello();
        } else {
            APLogger.LogError("TCPClient: Failed to connect to Cyberpunk AP Client server. Status code: " + ToString(status));
            this.isConnected = false;
        }
    }

    public cb func OnDisconnected() -> Void {
        APLogger.LogInfo( "Disconnected from Cyberpunk AP Client Server.");
        this.isConnected = false;
    }

    public cb func OnCommand(command: String) -> Void {
        //APLogger.LogInfo( "TCPClient: Server Response: " + command);
        //First check if were receiving a HELLO response from the server
        if StrContains(command, "HELLO:") {
            this.HandleHelloResponse(command);
        }
        if StrContains(command, "CONNECT_REQ:") {
            this.HandleAPConnectResponse(command);
        }
        if StrContains(command, "SYNC_ITEMS:") {
            this.HandleSyncItemsResponse(command);
        }
        if StrContains(command, "SYNC_CHECKS:"){
            this.HandleSyncCheck(command);
        }
        if StrContains(command, "OK_READY:") {
            this.HandleReadyResponse(command);
        }
        if StrContains(command, "DEATHLINK_RECEIVED") {
            this.HandleDeathLinkCommand(command);
        }
        if StrContains(command, "DEATHLINK_SEND:") {
            this.HandleDeathLinkSendCommand(command);
        }
        if StrContains(command, "ITEM_RECEIVED:") {
            this.HandleItemReceivedCommand(command);
        }
        if StrContains(command, "SYNC_CONFIG:") {
            this.HandleSyncConfigCommand(command);
        }
    }
/*
Below are methods for sendings specific commands to the server
*/

    public func SendSyncCheckRequest() -> Void {
        this.SendMessage("SYNC_CHECKS");
    } 

/*
Below is handler methods for processing incoming commands from the server.
*/
    private func HandleSyncCheck(command: String) -> Void {
        APLogger.LogInfo(s"Sync Check:\(command)");
        let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
        let parts: array<String> = StrSplit(command, ":");
        let locations: array<String> = StrSplit(parts[2], ",");

        if ArraySize(locations) > 0 {
            APGameSystem.HandleSyncCheck(locations);
        }
    }

    private func HandleCheckRequestResponse(command: String) -> Void {
        
    }

    private func HandleDeathLinkCommand(command: String) -> Void {
        //APLogger.LogInfo( "TCPClient: Received DeathLink command from server. Triggering player death.");
        if StrCmp(command, "DEATHLINK_RECEIVED") == 0 {
            //APLogger.LogInfo( "DeathLink command is valid");
            let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
            APGameSystem.HandleDeathLink();
        }
        else {
            APLogger.LogError( "TCPClient: Received Error: " + command);
        }
        
    }

    private func HandleDeathLinkSendCommand(command: String) -> Void {
        let parts: array<String> = StrSplit(command, ":");
        // Change this to >= 2 since we access parts[1]
        if ArraySize(parts) >= 2 { 
            if StrCmp(parts[0], "DEATHLINK_SEND") == 0 {
                if StrCmp(parts[1], "OK") == 0 {
                    //APLogger.LogInfo( "TCPClient: Server acknowledged DeathLink send.");
                } else {
                    APLogger.LogError( "TCPClient: Server did not acknowledge DeathLink send: " + command);
                }
            }
        } else {
            APLogger.LogError( "TCPClient: Received Error or Malformed Command: " + command);
        }
    }

    private func HandleItemReceivedCommand(command: String) -> Void {
        //APLogger.LogInfo( "TCPClient: Received Item Received command from server.");
        let parts: array<String> = StrSplit(command, ":");
        if ArraySize(parts) >= 2 {
            if StrCmp(parts[0], "ITEM_RECEIVED") == 0 {
                let itemName: String = parts[1];
                let senderName: String = parts[2];
                let itemDisplayName: String = parts[3];
                // Here you would add code to actually grant the item to the player in-game
                APLogger.LogInfo( s"Received \(itemDisplayName) from \(senderName)");
                let gameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
                gameSystem.HandleItemReceived(itemName);
                this.SendMessage(s"ITEM_RECEIVED:OK\r\n");
            } else {
                APLogger.LogError( "TCPClient: Received Error: " + command);
            }
        }
    }
/*
Below is the full handshake process
*/

    private func SendHello() -> Void {
        if IsDefined(this.socket) && this.isConnected {
            //APLogger.LogInfo( "TCPClient: Sending HELLO to server with client version " + this.APClientVersion);
            this.socket.SendCommand("HELLO:" + this.APClientVersion);
        }
    }

    private func HandleHelloResponse(response: String) -> Void {
    // Split the response by the colon ":"
        let parts: array<String> = StrSplit(response, ":");
        
        // Safety check: ensure we have exactly 3 parts (HELLO, Version, Status)
        if ArraySize(parts) == 3 {
            let command: String = parts[0];
            //let serverVersion: String = parts[1];
            let status: String = parts[2];
            
            // StrCmp returns 0 if the strings are identical
            if StrCmp(command, "HELLO") == 0 {
                
                if StrCmp(status, "OK") == 0 {
                    // Handshake successful! 
                    //APLogger.LogInfo( "TCPClient: Connected to server version " + serverVersion);
                    // Now that we've successfully completed the handshake, we can proceed to send our connection request with the slot name
                    this.SendAPConnectRequest();
                    
                } else if StrCmp(status, "FAIL") == 0 {
                    // Handshake failed! Alert the user.
                    APLogger.LogError( "TCPClient: Version mismatch! The server requires version " + this.CyberpunkTCPServerRequiredVersion + ". Please update from GitHub.");
                }
            }
        } else {
            APLogger.LogError( "TCPClient: Malformed HELLO response from server.");
        }
    }

    private func SendAPConnectRequest() -> Void {
        //APLogger.LogInfo( "TCPClient: Sending AP Connect Request for slot " + this.slotName);
        let payload: String = s"CONNECT_REQ:archipelago.gg:\(this.port):\(this.slotName)";
        this.SendMessage(payload);
    }

    private func HandleAPConnectResponse(response: String) -> Void {
        // Handle the server's response to the connection request
        //APLogger.LogInfo( "TCPClient: Received AP Connect Response: " + response);
        let parts: array<String> = StrSplit(response, ":");
        if ArraySize(parts) >= 2 {
            let command: String = parts[0];
            let status: String = parts[1];
            
            if StrCmp(command, "CONNECT_REQ") == 0 {
                if StrCmp(status, "OK") == 0 {
                    //APLogger.LogInfo( "TCPClient: Successfully connected to Archipelago server with slot " + this.slotName);
                    // Now that we're connected and authenticated, we can start sending/receiving game state updates
                    this.SendSyncItemsRequest();
                } else {
                    APLogger.LogError("TCPClient: Failed to connect to Archipelago server with slot " + this.slotName);
                }
            }
        } else {
            APLogger.LogError("TCPClient: Malformed CONNECT_RESP from server.");
        }
        // You can parse the response and take appropriate actions here
    }

    private func SendSyncItemsRequest() -> Void {
        //APLogger.LogInfo( "TCPClient: Sending SYNC_ITEMS request");
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        let totalItemCount: Int32;

        // Get the total NetworkItems received count from persistent storage
        // This tracks the index into the Python server's received_items list
        if IsDefined(APGameState) {
            for item in APGameState.items.Items {
                totalItemCount = totalItemCount + item.totalFromAP;
            }
        }
        else { 
            totalItemCount = 0;
        }

        let payload: String = s"SYNC_ITEMS:CURRENT_COUNT:\(totalItemCount)";
        this.SendMessage(payload);
    }

    private func HandleSyncItemsResponse(response: String) -> Void {
        //APLogger.LogInfo( "TCPClient: Received SYNC_ITEMS response: " + response);
        let parts: array<String> = StrSplit(response, ":");
        if ArraySize(parts) >= 2 {
            let command: String = parts[0];
            let itemsHeader: String = parts[1];
            let itemsString: String = parts[2];

            //APLogger.LogInfo( s"Command: \(command) itemsHeader: \(itemsHeader) itemsString: \(itemsString)");

            if StrCmp(command, "SYNC_ITEMS") == 0 {
                if StrCmp(itemsHeader, "ITEMS") == 0 {
                    //APLogger.LogInfo( "TCPClient: SYNC_ITEMS response contains item list.");
                    let items: array<String> = StrSplit(itemsString, ",");
                    let gameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;

                    if IsDefined(gameSystem) {
                        gameSystem.FeedItemsList(items);
                        // FeedItemsList already sends SYNC_COMPLETE response internally
                    } else {
                        APLogger.LogError("TCPClient: APGameSystem not available for item sync");
                    }

                    // After sync complete, request config
                    this.SendSyncConfigRequest();
                } else {
                    APLogger.LogError("TCPClient: Failed to Sync Items, is the client connected to an Archipelago server?");
                }
            }
        } else {
            APLogger.LogError("TCPClient: Malformed SYNC_ITEMS response from server.");
        }
    }

    private func SendSyncConfigRequest() -> Void {
        //APLogger.LogInfo( "TCPClient: Sending SYNC_CONFIG request");
        let payload: String = "SYNC_CONFIG";
        this.SendMessage(payload);
    }

    private func HandleSyncConfigCommand(command: String) -> Void {
        //APLogger.LogInfo( "TCPClient: Received SYNC_CONFIG command: " + command);
        let parts: array<String> = StrSplit(command, ":");
        if ArraySize(parts) >= 3 {
            //let commandType: String = parts[0];
            //let status: String = parts[1];
            let configData: String = "";
            let i: Int32 = 2;
            while i < ArraySize(parts) {
                if i == 2 {
                    configData = parts[i];
                } else {
                    configData = configData + "_" + parts[i];
                }
                i += 1;
            }
            
            let configOptions: array<String> = StrSplit(configData, ",");
            let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;

            
            for option in configOptions {
                //APLogger.LogInfo( s"Option: \(option)");
                if StrContains(option, "death_link") {
                    if StrContains(option, "true") {
                        APGameState.enableDeathLink = true;
                        APLogger.LogInfo( "Set Deathlink to Enabled");
                    }
                    else {
                        APGameState.enableDeathLink = false;
                    }
                    
                }
                if StrContains(option, "skill_points_as_items") { //Not implemented
                    if StrContains(option, "true") {
                        APGameState.skillPointsAsItems = true;
                    }
                    else {
                        APGameState.skillPointsAsItems = false;
                    }
                    
                }
            }
        }

        //Request a Sync
        let gameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
        gameSystem.SendSyncChecks();

    }

    private func HandleReadyResponse(response: String) -> Void {
        //APLogger.LogInfo( "TCPClient: Received OK_READY response from server: " + response);
        let parts = StrSplit(response, ":");
        if ArraySize(parts) >= 1 {
            if StrCmp(parts[0], "OK_READY") == 0 {
                //APLogger.LogInfo( "TCPClient: Server acknowledged ready signal. Starting game sync.");
                if (StrCmp(parts[1], "OK") == 0) {
                    APLogger.LogInfo( "Client TCP Handshake Complete");
                } else {
                    APLogger.LogWarning( "TCPClient: Server did not accept ready signal: " + response);
                }
            } else {
                APLogger.LogError("TCPClient: Received unexpected response to ready signal: " + response);
            }
        }
    }
}