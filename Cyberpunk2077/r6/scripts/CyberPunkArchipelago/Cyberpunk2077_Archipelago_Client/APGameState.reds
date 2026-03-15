module Archipelago

public class APGameState extends ScriptableService {
    public let diedFromDeathLink: Bool;
    public let skillPointsAsItems: Bool;
    public let enableDeathLink: Bool;
    let items: array<String>;
    let totalSkillPoints: Int32;

    public func OnAttach() -> Void {
        LogChannel(n"DEBUG", "Cyberpunk 2077 Archipelago Mod Ready");
    }

    public func FeedItemsList(itemList: array<String>) -> Void {
        this.items = itemList;
        //LogChannel(n"DEBUG", s"APGameState: Received \(ArraySize(itemList)) items from initial sync");
        for item in itemList {
            //LogChannel(n"DEBUG", "Item: " + item);
            // Process each item immediately during sync
            this.HandleItemReceived(item);
        }
    }

    public func ResyncData() -> Void {
        for item in this.items {
            this.HandleItemReceived(item);
        }
    }

    public func HandleItemReceived(item: String) -> Void {
        //LogChannel(n"DEBUG", "Received item: " + item);
        let parts: array<String> = StrSplit(item, "_");
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
            if StrCmp(itemType, "cw") == 0 {
                this.HandleCyberwareReceived(item);
            }
            if StrCmp(itemType, "sp") == 0 {
                this.HandleRecievedSkillPoint(item);
            }
            if StrCmp(itemType, "trp") == 0 {
                this.HandleTrapReceived(item);
            }
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

    public func DiedFromDeathLink() -> Void {
        this.diedFromDeathLink = true;
    }

    public func HandlePlayerRespawn() -> Void {
        //LogChannel(n"DEBUG", "APGameState: Player has respawned. Resetting DeathLink state.");
        this.diedFromDeathLink = false;
    }
}