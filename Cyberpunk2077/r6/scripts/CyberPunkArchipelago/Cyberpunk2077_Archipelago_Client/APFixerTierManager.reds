module Archipelago

// Tracks which fixer gig tiers the Fixers-Only goal has unlocked.
//
// Tier unlock items arrive as ordinary quest keys (ap_qk_<fixer>_tier_<n>), so
// APGameSystem.AddQuestKey already writes one fact per tier. Those facts are
// awkward to test from a quest phase or TweakDB condition, which can only compare
// a single fact against a number, so this manager also maintains one summary fact
// per fixer holding the highest tier that fixer has released
// (APConstants.GetFixerUnlockedTierFact). Tier 1 is granted as soon as the
// prologue is done, matching vanilla, where every fixer's first tier is available
// at street cred 1.
public class APFixerTierManager extends ScriptableSystem {
    private let questHandler: ref<APQuestHandler>;

    public func OnAttach() -> Void {
        let container: ref<ScriptableSystemsContainer> = this.GetGameInstance().GetScriptableSystemsContainer();
        this.questHandler = container.Get(n"Archipelago.APQuestHandler") as APQuestHandler;
        APLogger.LogDebug("APFixerTierManager initialized");
    }

    // Parse the fixer key out of an ap_qk_<fixer>_tier_<n> item ID.
    // Returns an empty string for any other quest key.
    public static func ParseFixerKey(itemId: String) -> String {
        let parts: array<String> = StrSplit(itemId, "_");
        if ArraySize(parts) != 5 {
            return "";
        }
        if StrCmp(parts[0], "ap") != 0 || StrCmp(parts[1], "qk") != 0 || StrCmp(parts[3], "tier") != 0 {
            return "";
        }
        if APConstants.GetFixerMaxTier(parts[2]) < 1 {
            return "";
        }
        return parts[2];
    }

    public static func IsFixerTierItem(itemId: String) -> Bool {
        return StrLen(APFixerTierManager.ParseFixerKey(itemId)) > 0;
    }

    // Highest tier this fixer has released, based on the per-tier unlock facts.
    // Returns 0 before the prologue, when even tier 1 is not yet open.
    public func GetUnlockedTier(fixer: String) -> Int32 {
        if !IsDefined(this.questHandler) || !this.questHandler.IsPassedPrologue() {
            return 0;
        }

        let unlocked: Int32 = 1;
        let tier: Int32 = 2;
        let maxTier: Int32 = APConstants.GetFixerMaxTier(fixer);
        while tier <= maxTier {
            if this.questHandler.HasQuestKey(APConstants.GetFixerTierFact(fixer, tier)) {
                unlocked = tier;
            }
            tier += 1;
        }
        return unlocked;
    }

    // Recompute every fixer's summary fact. Safe to call repeatedly: it only
    // writes facts and does so idempotently, so connect, resync and save load all
    // converge on the same state.
    public func RefreshUnlockedTierFacts() -> Void {
        if !IsDefined(this.questHandler) {
            APLogger.LogDebug("APFixerTierManager: Cannot refresh tier facts - quest handler not available");
            return;
        }

        let fixers: array<String> = APConstants.GetFixerKeys();
        for fixer in fixers {
            let unlocked: Int32 = this.GetUnlockedTier(fixer);
            if unlocked >= 1 {
                // Vanilla opens every fixer's tier 1 at street cred 1, so grant it
                // outright rather than spending a multiworld item on it.
                this.questHandler.SetQuestKey(APConstants.GetFixerTierFact(fixer, 1));
            }
            this.questHandler.SetQuestFact(APConstants.GetFixerUnlockedTierFact(fixer), unlocked);
        }
    }

    // Called when a tier unlock item arrives so the summary facts follow
    // immediately instead of waiting for the next sync.
    public func HandleFixerTierUnlock(itemId: String) -> Void {
        let fixer: String = APFixerTierManager.ParseFixerKey(itemId);
        if StrLen(fixer) == 0 {
            return;
        }

        this.RefreshUnlockedTierFacts();
        APLogger.LogInfo(s"Fixer gig tier unlocked: \(itemId) (\(fixer) now at tier \(ToString(this.GetUnlockedTier(fixer))))");
    }
}
