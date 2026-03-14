module Archipelago
import RedSocket.*

public class TCPClient extends ScriptableService { 
    private let socketService: ref<APRedSocketTCPService>;

    public func SendDeathLink() -> Void {

        if IsDefined(this.socketService) && this.socketService.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Sending DeathLink message to server.");
            let payload: String = "DEATHLINK_SEND";
            this.socketService.SendMessage(payload);
        } else {
            LogChannel(n"DEBUG", "TCPClient: ERROR - Cannot send DeathLink, socket is closed!");
        }
    }

    public func SendCheck(checkString: String) -> Void {
        if IsDefined(this.socketService) && this.socketService.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Sending Check message to server: " + checkString);
            let payload: String = s"CHECK:\(checkString)";
            this.socketService.SendMessage(payload);
        } else {
            LogChannel(n"DEBUG", "TCPClient: ERROR - Cannot send Check, socket is closed!");
        }
    }

    public func ConnectFromCET(ip: String, port: Int32, slotName: String) -> Void {
        LogChannel(n"DEBUG", s"TCPClient: ConnectFromCET called with IP: \(ip), Port: \(port), SlotName: \(slotName)");

        if port < 0 || port > 65535 {
            LogChannel(n"DEBUG", "TCPClient: ERROR - Invalid port number. Must be between 0 and 65535.");
            return;
        }

        this.AttemptConnectionToAPServer(ip, Cast<Uint16>(port), slotName);
    }

    public func SendReadySignal() -> Void {
        if IsDefined(this.socketService) && this.socketService.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Sending Ready Signal to server.");
            let payload: String = "OK_READY";
            this.socketService.SendMessage(payload);
        } else {
            LogChannel(n"DEBUG", "TCPClient: ERROR - Cannot send Ready Signal, socket is closed!");
        }
    }

    private func AttemptConnectionToAPServer(ip: String, port: Uint16, slotName: String) -> Void {
        if !IsDefined(this.socketService) {
            this.socketService = new APRedSocketTCPService();
            this.socketService.Initialize(ip, port, slotName);
            this.socketService.Connect();
        } else {
            LogChannel(n"DEBUG", "TCPClient: Socket service already initialized. Ignoring duplicate connection attempt.");
        }
    }

    public func DisconnectFromCET() -> Void {
        if IsDefined(this.socketService) {
            this.socketService.Disconnect();
            this.socketService = null;
        }
    }
}

public class APRedSocketTCPService extends IScriptable {
    // The actual underlying RedSocket instance
    private let socket: ref<Socket>; 

    // Connection state
    private let ip: String = "";
    private let port: Uint16;
    public let isConnected: Bool = false;
    private let slotName: String = "";
    private let APClientVersion: String = "0.1.0";
    private let CyberpunkTCPServerRequiredVersion: String = "0.1.0";

    // 1. Initialize and configure the wrapper
    public final func Initialize(targetIp: String, targetPort: Uint16, slotName: String) -> Void {
        this.ip = targetIp;
        this.port = targetPort;
        this.slotName = slotName;

        // Instantiate the raw RedSocket object
        this.socket = Socket.Create(); 
        
        LogChannel(n"DEBUG", s"TCPClient: Configured for \(this.ip):\(this.port)");
    }

    // 2. Open the connection
    public final func Connect() -> Void {
        if IsDefined(this.socket) && !this.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Attempting Connection to TCP Server at " + this.ip + ":" + ToString(this.port));
            
            this.socket.RegisterListener(this, n"OnCommand", n"OnConnected", n"OnDisconnected");

            // Call RedSocket's native connect method
            this.socket.Connect(this.ip, this.port);
            this.isConnected = true;
        }
    }

    // 3. Send a JSON payload to the AP Server
    public final func SendMessage(payload: String) -> Void {
        if IsDefined(this.socket) && this.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Sending message to server: " + payload);
            this.socket.SendCommand(payload);
        } else {
            LogChannel(n"DEBUG", "TCPClient: ERROR - Cannot send message, socket is closed!");
        }
    }

    // 4. Safely close the connection (Crucial for when the player quits to desktop)
    public final func Disconnect() -> Void {
        if IsDefined(this.socket) && this.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Closing connection.");
            this.socket.Disconnect();
            this.isConnected = false;
        }
    }

    public cb func OnConnected(status: Int32) -> Void {
        LogChannel(n"DEBUG", "TCPClient: Status recieved");
        if status == 0 {
            LogChannel(n"DEBUG", "TCPClient: Successfully connected to Cyberpunk AP Client server.");
            this.isConnected = true;
            this.SendHello();
        } else {
            LogChannel(n"DEBUG", "TCPClient: Failed to connect to Cyberpunk AP Client server. Status code: " + ToString(status));
            this.isConnected = false;
        }
    }

    public cb func OnDisconnected() -> Void {
        LogChannel(n"DEBUG", "TCPClient: Disconnected from Archipelago server.");
        this.isConnected = false;
    }

    public cb func OnCommand(command: String) -> Void {
        LogChannel(n"DEBUG", "TCPClient: Server Response: " + command);
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
    }
/*
Below is handler methods for processing incoming commands from the server.
*/
    private func HandleDeathLinkCommand(command: String) -> Void {
        LogChannel(n"DEBUG", "TCPClient: Received DeathLink command from server. Triggering player death.");
        if StrCmp(command, "DEATHLINK_RECEIVED") == 0 {
            LogChannel(n"DEBUG", "DeathLink command is valid");
            let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
            APGameSystem.HandleDeathLink();
        }
        else {
            LogChannel(n"WARN", "TCPClient: Received Error: " + command);
        }
        
    }

    private func HandleDeathLinkSendCommand(command: String) -> Void {
        let parts: array<String> = StrSplit(command, ":");
        // Change this to >= 2 since we access parts[1]
        if ArraySize(parts) >= 2 { 
            if StrCmp(parts[0], "DEATHLINK_SEND") == 0 {
                if StrCmp(parts[1], "OK") == 0 {
                    LogChannel(n"DEBUG", "TCPClient: Server acknowledged DeathLink send.");
                } else {
                    LogChannel(n"WARN", "TCPClient: Server did not acknowledge DeathLink send: " + command);
                }
            }
        } else {
            LogChannel(n"WARN", "TCPClient: Received Error or Malformed Command: " + command);
        }
    }

    private func HandleItemReceivedCommand(command: String) -> Void {
        LogChannel(n"DEBUG", "TCPClient: Received Item Received command from server.");
        let parts: array<String> = StrSplit(command, ":");
        if ArraySize(parts) >= 2 {
            if StrCmp(parts[0], "ITEM_RECEIVED") == 0 {
                let itemName: String = parts[1];
                let senderName: String = parts[2];
                LogChannel(n"DEBUG", "TCPClient: Item received from server: " + itemName + " sent by " + senderName);
                // Here you would add code to actually grant the item to the player in-game
                let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
                APGameState.HandleItemReceived(itemName);
                this.SendMessage(s"ITEM_RECEIVED:OK\r\n");
            } else {
                LogChannel(n"WARN", "TCPClient: Received Error: " + command);
            }
        }
    }
/*
Below is the full handshake process
*/

    private func SendHello() -> Void {
        if IsDefined(this.socket) && this.isConnected {
            LogChannel(n"DEBUG", "TCPClient: Sending HELLO to server with client version " + this.APClientVersion);
            this.socket.SendCommand("HELLO:" + this.APClientVersion);
        }
    }

    private func HandleHelloResponse(response: String) -> Void {
    // Split the response by the colon ":"
        let parts: array<String> = StrSplit(response, ":");
        
        // Safety check: ensure we have exactly 3 parts (HELLO, Version, Status)
        if ArraySize(parts) == 3 {
            let command: String = parts[0];
            let serverVersion: String = parts[1];
            let status: String = parts[2];
            
            // StrCmp returns 0 if the strings are identical
            if StrCmp(command, "HELLO") == 0 {
                
                if StrCmp(status, "OK") == 0 {
                    // Handshake successful! 
                    LogChannel(n"DEBUG", "TCPClient: Connected to server version " + serverVersion);
                    // Now that we've successfully completed the handshake, we can proceed to send our connection request with the slot name
                    this.SendAPConnectRequest();
                    
                } else if StrCmp(status, "FAIL") == 0 {
                    // Handshake failed! Alert the user.
                    LogChannel(n"WARN", "TCPClient: Version mismatch! The server requires version " + this.CyberpunkTCPServerRequiredVersion + ". Please update from GitHub.");
                }
            }
        } else {
            LogChannel(n"ERROR", "TCPClient: Malformed HELLO response from server.");
        }
    }

    private func SendAPConnectRequest() -> Void {
        LogChannel(n"DEBUG", "TCPClient: Sending AP Connect Request for slot " + this.slotName);
        let payload: String = s"CONNECT_REQ:archipelago.gg:\(this.port):\(this.slotName)";
        this.SendMessage(payload);
    }

    private func HandleAPConnectResponse(response: String) -> Void {
        // Handle the server's response to the connection request
        LogChannel(n"DEBUG", "TCPClient: Received AP Connect Response: " + response);
        let parts: array<String> = StrSplit(response, ":");
        if ArraySize(parts) >= 2 {
            let command: String = parts[0];
            let status: String = parts[1];
            
            if StrCmp(command, "CONNECT_REQ") == 0 {
                if StrCmp(status, "OK") == 0 {
                    LogChannel(n"DEBUG", "TCPClient: Successfully connected to Archipelago server with slot " + this.slotName);
                    // Now that we're connected and authenticated, we can start sending/receiving game state updates
                    this.SendSyncItemsRequest();
                } else {
                    LogChannel(n"WARN", "TCPClient: Failed to connect to Archipelago server with slot " + this.slotName);
                }
            }
        } else {
            LogChannel(n"ERROR", "TCPClient: Malformed CONNECT_RESP from server.");
        }
        // You can parse the response and take appropriate actions here
    }

    private func SendSyncItemsRequest() -> Void {
        LogChannel(n"DEBUG", "TCPClient: Sending SYNC_ITEMS request");
        let payload: String = "SYNC_ITEMS";
        this.SendMessage(payload);
    }

    private func HandleSyncItemsResponse(response: String) -> Void {
        LogChannel(n"DEBUG", "TCPClient: Received SYNC_ITEMS response: " + response);
        let parts: array<String> = StrSplit(response, ":");
        if ArraySize(parts) >= 2 {
            let command: String = parts[0];
            let itemsHeader: String = parts[1];
            let itemsString: String = parts[2];
            
            if StrCmp(command, "SYNC_ITEMS") == 0 {
                if StrCmp(itemsHeader, "ITEMS") == 0 {
                    LogChannel(n"DEBUG", "TCPClient: SYNC_ITEMS response contains item list.");
                    let items: array<String> = StrSplit(itemsString, ",");
                    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
                    APGameState.FeedItemsList(items);
                } else {
                    LogChannel(n"WARN", "TCPClient: SYNC_ITEMS response does not contain item list.");
                }

            }
        } else {
            LogChannel(n"ERROR", "TCPClient: Malformed SYNC_ITEMS response from server.");
        }
    }

    private func HandleReadyResponse(response: String) -> Void {
        LogChannel(n"DEBUG", "TCPClient: Received OK_READY response from server: " + response);
        let parts = StrSplit(response, ":");
        if ArraySize(parts) >= 1 {
            if StrCmp(parts[0], "OK_READY") == 0 {
                LogChannel(n"DEBUG", "TCPClient: Server acknowledged ready signal. Starting game sync.");
                if (StrCmp(parts[1], "OK") == 0) {
                    LogChannel(n"DEBUG", "TCPClient: Ready signal accepted by server. You are now synced and will receive item updates.");
                } else {
                    LogChannel(n"WARN", "TCPClient: Server did not accept ready signal: " + response);
                }
            } else {
                LogChannel(n"WARN", "TCPClient: Received unexpected response to ready signal: " + response);
            }
        }
    }
}