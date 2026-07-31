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
        APLogger.LogDebug(s"APQuestHandler: SetQuestKey('\(questKeyId)') -> fact now reads \(questSystem.GetFact(StringToName(questKeyId)))");
        return true;
    }

    // Check if a quest key is set
    public func HasQuestKey(questKeyId: String) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());

        if IsDefined(questSystem) {
            let factValue: Int32 = questSystem.GetFact(StringToName(questKeyId));
            APLogger.LogDebug(s"APQuestHandler: HasQuestKey('\(questKeyId)') - raw fact value=\(factValue)");
            return factValue >= 1;
        }
        APLogger.LogDebug(s"APQuestHandler: HasQuestKey('\(questKeyId)') - quest system not available, returning false");
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
        let q000Done: Int32 = this.GetQuestFact(APConstants.GetQuestQ000Done());
        let q001Done: Int32 = this.GetQuestFact(APConstants.GetQuestQ001Done());
        let firestormDone: Int32 = this.GetQuestFact(APConstants.GetQuestQ101_01_firestormDone());
        let vPills: Int32 = this.GetQuestFact(APConstants.GetVPillsFact());
        let result: Bool = q000Done > 0 && q001Done > 0 && firestormDone > 0 && vPills > 0;
        APLogger.LogDebug(
            s"APQuestHandler: IsPassedPrologue - q000Done=\(q000Done), q001Done=\(q001Done), firestormDone=\(firestormDone), vPills=\(vPills) -> \(result)"
        );
        return result;
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
