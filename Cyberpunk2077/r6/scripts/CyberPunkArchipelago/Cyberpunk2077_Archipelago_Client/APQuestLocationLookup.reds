module Archipelago

// Static quest->location alias table for quest completion checks.
// Keep this explicit (no generated mappings) so game-side behavior is predictable.
public class APQuestLocationLookup {

    // Resolve the location check ID to send for a completed quest.
    // Returns an empty string when the quest should not emit a check.
    public static func ResolveLocationId(questId: String) -> String {
        if StrLen(questId) == 0 {
            return "";
        }

        // Lifepath intros all correspond to one Archipelago location.
        if StrCmp(questId, "q000_corpo") == 0
            || StrCmp(questId, "q000_nomad") == 0
            || StrCmp(questId, "q000_street_kid") == 0 {
            return "q000_street_kid";
        }

        // Endings all correspond to one Archipelago location.
        if StrCmp(questId, "q202_nomads") == 0
            || StrCmp(questId, "q203_legend") == 0
            || StrCmp(questId, "q204_reborn") == 0
            || StrCmp(questId, "q307_tomorrow") == 0 {
            return "q201_heir";
        }

        // Phantom Liberty Firestarter path split (Reed path completions).
        if StrCmp(questId, "q305_prison_convoy") == 0 {
            return "pl_split_quest_1";
        }
        if StrCmp(questId, "q305_bunker") == 0 {
            return "pl_split_quest_2";
        }
        if StrCmp(questId, "q305_border_crossing") == 0 {
            return "pl_split_quest_3";
        }

        // Songbird path: Killing Moon uses Active/Succeeded handlers in OnJournalUpdate.
        if StrCmp(questId, "q306_devils_bargain") == 0 {
            return "";
        }

        // Act 3 pre-Nocturne branches — intermediate quests, not tracked separately.
        if StrCmp(questId, "q113_rescuing_hanako") == 0
            || StrCmp(questId, "q113_corpo") == 0 {
            return "";
        }

        // Act 3 ending-path quests — epilogues (q201_heir aliases) cover "Ending Reached".
        if StrCmp(questId, "q114_01_nomad_initiation") == 0
            || StrCmp(questId, "q114_02_maglev_line_assault") == 0
            || StrCmp(questId, "q114_03_attack_on_arasaka_tower") == 0
            || StrCmp(questId, "q115_afterlife") == 0
            || StrCmp(questId, "q115_rogues_last_flight") == 0
            || StrCmp(questId, "q116_cyberspace") == 0
            || StrCmp(questId, "09_solo") == 0 {
            return "";
        }

        return questId;
    }

    // Send a location check once (idempotent via ap_<locationId> quest facts).
    public static func SendLocationCheck(questSystem: ref<QuestsSystem>, tcpService: ref<TCPClient>, locationId: String) -> Void {
        if !IsDefined(questSystem) || !IsDefined(tcpService) || StrLen(locationId) == 0 {
            return;
        }

        let factName: CName = StringToName(s"ap_\(locationId)");
        if questSystem.GetFact(factName) >= 1 {
            return;
        }

        questSystem.SetFact(factName, 1);
        tcpService.SendCheck(locationId);

        // Notify the AP server of goal completion so remaining slot checks can release.
        if StrCmp(locationId, "q201_heir") == 0 {
            let storyCompleteFact: CName = StringToName("ap_story_complete_sent");
            if questSystem.GetFact(storyCompleteFact) < 1 {
                if AP_StoryComplete() {
                    questSystem.SetFact(storyCompleteFact, 1);
                }
            }
        }
    }
}
