module Archipelago

// Reports goal completion for the Fixers-Only goal.
//
// Every other goal finishes at an ending epilogue, which APQuestLocationLookup
// reports directly. Fixers-Only instead finishes when every gig in
// gig_goal_manifest has been cleared, so this walks the manifest against the
// ap_<locationId> facts that record already-sent checks.
public class APGigGoalTracker {

    // Number of manifest gigs still outstanding, or -1 when the manifest has not
    // arrived yet (not connected, or not a Fixers-Only run).
    public static func CountRemainingGigs(questSystem: ref<QuestsSystem>, gameState: ref<APGameState>) -> Int32 {
        if !IsDefined(questSystem) || !IsDefined(gameState) || !gameState.IsFixersOnlyGoal() {
            return -1;
        }

        let total: Int32 = ArraySize(gameState.gigGoalIds);
        if total == 0 {
            return -1;
        }

        let remaining: Int32 = 0;
        for gigId in gameState.gigGoalIds {
            if questSystem.GetFact(StringToName(s"ap_\(gigId)")) < 1 {
                remaining += 1;
            }
        }
        return remaining;
    }

    // Tell the server the goal is met once the last gig is done. Idempotent via
    // the same fact the ending-based goals use, so a resync cannot re-send it.
    public static func ReportGoalIfComplete(questSystem: ref<QuestsSystem>, gameState: ref<APGameState>) -> Void {
        let remaining: Int32 = APGigGoalTracker.CountRemainingGigs(questSystem, gameState);
        if remaining < 0 {
            return;
        }

        let storyCompleteFact: CName = StringToName(APConstants.GetStoryCompleteSentFact());
        if questSystem.GetFact(storyCompleteFact) >= 1 {
            return;
        }

        if remaining > 0 {
            APLogger.LogDebug(s"Fixers-Only: \(ToString(remaining)) of \(ToString(ArraySize(gameState.gigGoalIds))) gig(s) remaining");
            return;
        }

        APLogger.LogInfo("Fixers-Only: every gig cleared - reporting goal completion");
        if AP_StoryComplete() {
            questSystem.SetFact(storyCompleteFact, 1);
        }
    }
}
