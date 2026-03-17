module Archipelago

public class APGameState extends ScriptableService { 
    public let diedFromDeathLink: Bool;
    public let skillPointsAsItems: Bool;
    public let enableDeathLink: Bool;
    public let items: ref<APItemList>;
    let totalSkillPoints: Int32;

    public func OnAttach() -> Void {
        LogChannel(n"INFO", "Cyberpunk 2077 Archipelago Mod Ready");
        this.items = new APItemList();
    }

    public func GetItems() -> ref<APItemList> {
        return this.items;
    }

    public func FeedItemsList(itemList: array<String>) -> Void {
        //LogChannel(n"DEBUG", s"=== FeedItemsList CALLED with \(ArraySize(itemList)) items ===");

        if !IsDefined(this.items) {
            this.items = new APItemList();
        }

        //LogChannel(n"DEBUG", s"this.items is defined: \(IsDefined(this.items))");
        for item in itemList {
            // Skip empty strings (happens when server sends SYNC_ITEMS:ITEMS: with no items)
            if StrLen(item) >= 0 {
                // Process each item immediately during sync
                this.HandleItemSync(item);
            }
            //LogChannel(n"DEBUG", "Item: " + item);
            
        }
        let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        tcpService.SendSyncCompleteResponse(ArraySize(this.items.Items));
        //LogChannel(n"DEBUG", s"Item Array Size of \(ArraySize(this.items.Items))");
        //LogChannel(n"DEBUG", s"=== FeedItemsList COMPLETED ===");
    }

    public func HandleItemSync(item: String) -> Void {
        //LogChannel(n"DEBUG", "Sync item: " + item);
        let parts: array<String> = StrSplit(item, "_");
        if ArraySize(parts) >= 2 {
            let apSignature = parts[0];
            let itemType = parts[1];
            if StrCmp(apSignature, "ap") != 0 {
                //LogChannel(n"DEBUG", "Invalid item signature: " + apSignature);
                return;
            }
            if StrCmp(itemType, "qk") == 0 { //Quests keys dont really matter cause they're just 1 or 0
                this.HandleQuestKeyReceived(item);
            }
            if StrCmp(itemType, "sp") == 0 { // Not working regardless
                //this.HandleRecievedSkillPoint(item);
            }
            //if StrCmp(itemType, "trp") == 0 { //Im not that evil lol.
            //    this.HandleTrapReceived(item);
            //}
            if StrCmp(itemType, "ed") == 0 {
                //LogChannel(n"DEBUG", s"Adding Eddies of amount: \(parts[3])");
                let amount: Int32 = StringToInt(parts[3]);
                this.items.AddItem("Items.money", amount);
            }
            if StrCmp(itemType, "inv") == 0 {
                let itemId: String = parts[2];
                //LogChannel(n"DEBUG", s"item is Inventory Item \(itemId)");
                this.items.AddItem(itemId, 1);
            }
        }
    }

    public func HandleItemReceived(item: String) -> Void {
        let parts: array<String> = StrSplit(item, "_");
        //LogChannel(n"DEBUG", s"Received Item \(item)");
        if ArraySize(parts) >= 2 {
            let apSignature = parts[0];
            let itemType = parts[1];
            if StrCmp(apSignature, "ap") != 0 {
                //LogChannel(n"DEBUG", "Invalid item signature: " + apSignature);
                return;
            }
            if StrCmp(itemType, "qk") == 0 {
                this.HandleQuestKeyReceived(item);
            }
            if StrCmp(itemType, "sp") == 0 {
                this.HandleRecievedSkillPoint(item);
            }
            if StrCmp(itemType, "trp") == 0 {
                this.HandleTrapReceived(item);
            }
            if StrCmp(itemType, "ed") == 0 {
                this.HandleEddiesReceived(item);
            }
            if StrCmp(itemType, "inv") == 0 {
                this.HandleInventoryItemReceived(item);
            }

            // NOTE: Do NOT increment totalItemsReceived here!
            // Queue worker sends items that are ALREADY in server's received_items list
            // Only FeedItemsList should increment (during SYNC_ITEMS)
        }
    }

    public func HandleInventoryItemReceived(item: String) -> Void {
        let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
        let parts : array<String> = StrSplit(item, "_");
        let itemID: String = "";
        if ArraySize(parts) > 2 { //This is because some Item IDs in the game have _ in the item id, this makes sure it keeps the item ID in tact
            let i: Int32 = 2; 
            
            while i < ArraySize(parts) {
                if i == 2 {
                    itemID = parts[i];
                } else {
                    itemID = itemID + "_" + parts[i];
                }
                i += 1;
            }
        }
        
        if IsDefined(this.items) {
            this.items.AddItem(itemID, 1);
        }

        if IsDefined(APGameSystem) {
            APGameSystem.AddInventoryItem(itemID);
        }
    }

    public func HandleQuestKeyReceived(questKey: String) -> Void {
        //LogChannel(n"DEBUG", "Handling received quest key: " + questKey);
        let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
        if IsDefined(APGameSystem) {
            APGameSystem.AddQuestKey(questKey);
        }
    }

    public func HandleCyberwareReceived(cyberware: String) -> Void {
        //LogChannel(n"DEBUG", "Handling received cyberware: " + cyberware);
    }

    public func HandleRecievedSkillPoint(skillPoint: String) -> Void {
        //LogChannel(n"DEBUG", "Handling received skill point: " + skillPoint);
    }

    public func HandleTrapReceived(trapName: String) -> Void {
        //LogChannel(n"DEBUG", "Handling received trap: " + trapName);
    }

    public func HandleEddiesReceived(eddies: String) -> Void {
        let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
        let parts: array<String> = StrSplit(eddies, "_");
        let amount: Int32 = StringToInt(parts[3]);
        
        if IsDefined(this.items) {
            this.items.AddItem("Items.money", amount);
        }


        APGameSystem.AddEddies(amount);
    }

    public func DiedFromDeathLink() -> Void {
        this.diedFromDeathLink = true;
    }

    public func HandlePlayerRespawn() -> Void {
        //LogChannel(n"DEBUG", "APGameState: Player has respawned. Resetting DeathLink state.");
        this.diedFromDeathLink = false;
    }
}
