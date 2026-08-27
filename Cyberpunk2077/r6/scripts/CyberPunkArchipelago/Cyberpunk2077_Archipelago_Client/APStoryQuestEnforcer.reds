module Archipelago

// Decides which quests count for the Fixers-Only goal.
//
// Cyberpunk drives story availability from quest phase graphs rather than
// TweakDB, and an activated journal entry cannot be withdrawn, so the client
// cannot cancel a story quest that has already started. What it can do is refuse
// to treat story progress as Archipelago progress, and publish facts that quest
// phase and TweakDB conditions read so blocked content is never offered in the
// first place. See vendor_checks_README.md's sibling fixer_gigs_README.md for
// that side of the gate.
//
// The allow-list comes from the gig_goal_manifest slot_data field rather than
// from quest ID patterns, so it always matches exactly what the seed generated.
public class APStoryQuestEnforcer {

    // The lifepath intros resolve to a single check that Fixers-Only keeps,
    // because the prologue stays playable and every district entrance in the
    // generation logic hangs off it.
    public static func GetLifepathLocationId() -> String { return "q000_street_kid"; }

    public static func IsGigGoalCheck(gameState: ref<APGameState>, locationId: String) -> Bool {
        if !IsDefined(gameState) {
            return false;
        }
        return ArrayContains(gameState.gigGoalIds, locationId);
    }

    // True when this check belongs to a Fixers-Only run. Vendor checks are not
    // quests and never reach this path, so only gigs and the lifepath check pass.
    public static func IsRunCheck(gameState: ref<APGameState>, locationId: String) -> Bool {
        return StrCmp(locationId, APStoryQuestEnforcer.GetLifepathLocationId()) == 0
            || APStoryQuestEnforcer.IsGigGoalCheck(gameState, locationId);
    }

    // Record that a story check was reached but does not count, and tell the
    // player why. Idempotent: the fact doubles as the "already warned" marker.
    public static func HandleBlockedStoryCheck(game: GameInstance, questId: String) -> Void {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game) as QuestsSystem;
        if !IsDefined(questSystem) {
            return;
        }

        let blockedFact: CName = StringToName(APConstants.GetStoryBlockedFact(questId));
        if questSystem.GetFact(blockedFact) >= 1 {
            return;
        }
        questSystem.SetFact(blockedFact, 1);

        APLogger.LogInfo(s"Fixers-Only: \(questId) is not part of this run - no check sent");

        let gameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(APConstants.GetAPGameStateName()) as APGameState;
        if !IsDefined(gameState) {
            return;
        }
        let phoneSystem: ref<APPhoneSystem> = gameState.GetPhoneSystem();
        if IsDefined(phoneSystem) {
            let player: ref<GameObject> = GameInstance.GetPlayerSystem(game).GetLocalPlayerMainGameObject();
            phoneSystem.SendStoryBlockedNotification(player);
        }
    }
}
