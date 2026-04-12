module Archipelago

// Handles quest-related operations
// Separates quest system integration from other concerns
// Uses ScriptableSystem pattern for proper lifecycle management
public class APQuestHandler extends ScriptableSystem {

    public func OnAttach() -> Void {
        APLogger.LogDebug("APQuestHandler initialized");
    }

    // Set a quest key (unlock item)
    public func SetQuestKey(questKeyId: String) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if !IsDefined(questSystem) {
            APLogger.LogDebug("APQuestHandler: Cannot set quest key - quest system not available");
            return false;
        }

        questSystem.SetFact(StringToName(questKeyId), 1);
        return true;
    }

    // Check if a quest key is set
    public func HasQuestKey(questKeyId: String) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if IsDefined(questSystem) {
            return questSystem.GetFact(StringToName(questKeyId)) >= 1;
        }
        return false;
    }

    // Get a quest fact value
    public func GetQuestFact(factName: String) -> Int32 {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if IsDefined(questSystem) {
            return questSystem.GetFact(StringToName(factName));
        }
        return 0;
    }

    // Set a quest fact value
    public func SetQuestFact(factName: String, value: Int32) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if !IsDefined(questSystem) {
            APLogger.LogDebug("APQuestHandler: Cannot set quest fact - quest system not available");
            return false;
        }

        questSystem.SetFact(StringToName(factName), value);
        return true;
    }

    // Register a quest listener
    public func RegisterQuestListener(factName: CName, listener: ref<IScriptable>, callbackName: CName) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if !IsDefined(questSystem) {
            APLogger.LogDebug("APQuestHandler: Cannot register listener - quest system not available");
            return false;
        }

        questSystem.RegisterListener(factName, listener, callbackName);
        return true;
    }

    // Check if heist intro is complete (used for district enforcement)
    public func IsPassedPrologue() -> Bool {
        return this.GetQuestFact(APConstants.GetQuestQ000Done()) > 0 && 
        this.GetQuestFact(APConstants.GetQuestQ001Done()) > 0 && 
        this.GetQuestFact(APConstants.GetQuestQ101_01_firestormDone()) > 0 &&
        this.GetQuestFact(APConstants.GetVPillsFact()) > 0;
    }

    // Send a location check to the server
    public func SendLocationCheck(locationId: String) -> Void {
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(APConstants.GetTCPClientName()) as TCPClient;

        if IsDefined(tcpClient) {
            // Mark as checked in quest system
            this.SetQuestFact(s"ap_\(locationId)", 1);

            // Send to server
            tcpClient.SendCheck(locationId);
        } else {
            APLogger.LogDebug("APQuestHandler: Cannot send check - TCP client not available");
        }
    }
}
