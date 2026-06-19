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

        // Songbird path: Killing Moon uses Active/Succeeded handlers in HandleJournalStateChange (APGameSystem).
        if StrCmp(questId, "q306_devils_bargain") == 0 {
            return "";
        }

        return questId;
    }

    // Extract a quest id from a journal path-like string.
    // Supports both slash styles because journal paths can be serialized either way.
    public static func ExtractQuestIdFromPath(pathValue: String) -> String {
        if StrLen(pathValue) == 0 {
            return "";
        }

        let questId: String = StrAfterLast(pathValue, "/");
        if StrLen(questId) > 0 {
            return questId;
        }

        return StrAfterLast(pathValue, "\\");
    }

    // Guards against sending unknown/non-world checks.
    public static func IsKnownLocationId(locationId: String) -> Bool {
        return APArchipelagoIdMappings.ResolveLocationAddress(locationId) >= 0l;
    }

    // Unified completion handler used by all quest completion hooks.
    public static func HandleSucceededQuest(questSystem: ref<QuestsSystem>, tcpService: ref<TCPClient>, questId: String) -> Void {
        if StrLen(questId) == 0 {
            return;
        }

        let locationId: String = APQuestLocationLookup.ResolveLocationId(questId);
        if StrLen(locationId) == 0 {
            return;
        }

        if !APQuestLocationLookup.IsKnownLocationId(locationId) {
            return;
        }

        APQuestLocationLookup.SendLocationCheck(questSystem, tcpService, locationId);
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
    }
}
