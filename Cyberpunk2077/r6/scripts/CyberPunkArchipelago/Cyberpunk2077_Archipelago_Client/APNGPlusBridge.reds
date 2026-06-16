module Archipelago

// Optional bridge for CyberpunkNewGamePlus integration.
// Uses persisted quest facts so this file remains safe when NG+ is not installed.
public class APNGPlusBridge {

    // 0 = not NG+ (or unsupported start), 1 = release base prologue chain,
    // 2 = release base prologue chain + q101_resurrection
    private static func GetPrologueReleaseMode(questSystem: ref<QuestsSystem>) -> Int32 {
        if !IsDefined(questSystem) {
            return 0;
        }

        let standaloneStart: Int32 = questSystem.GetFact(StringToName(APConstants.GetNGPlusStandaloneQ101StartFact()));
        if standaloneStart >= 1 {
            return 2;
        }

        let ngPlusActive: Int32 = questSystem.GetFact(StringToName(APConstants.GetNGPlusActiveFact()));
        if ngPlusActive < 1 {
            return 0;
        }

        let q001Start: Int32 = questSystem.GetFact(StringToName(APConstants.GetNGPlusQ001StartFact()));
        if q001Start == 0 {
            // Q101 start skips the prologue chain checks.
            return 2;
        }

        // Q001 start can naturally emit checks from journal progression.
        return 0;
    }

    private static func BuildPrologueLocationIds(mode: Int32) -> array<String> {
        let locationIds: array<String>;

        if mode < 1 {
            return locationIds;
        }

        ArrayPush(locationIds, "q000_street_kid");
        ArrayPush(locationIds, "q001_intro");
        ArrayPush(locationIds, "q001_01_victor");
        ArrayPush(locationIds, "q001_02_dex");
        ArrayPush(locationIds, "q003_maelstrom");
        ArrayPush(locationIds, "q004_braindance");
        ArrayPush(locationIds, "q005_heist");
        ArrayPush(locationIds, "q101_01_firestorm");

        if mode >= 2 {
            ArrayPush(locationIds, "q101_resurrection");
        }

        return locationIds;
    }

    private static func ReleasePrologueChecks(questSystem: ref<QuestsSystem>, tcpClient: ref<TCPClient>, mode: Int32) -> Int32 {
        let releasedCount: Int32 = 0;
        let locationIds: array<String> = APNGPlusBridge.BuildPrologueLocationIds(mode);
        let locationId: String;

        for locationId in locationIds {
            let factName: CName = StringToName(s"ap_\(locationId)");
            if questSystem.GetFact(factName) < 1 {
                APQuestLocationLookup.SendLocationCheck(questSystem, tcpClient, locationId);
                releasedCount += 1;
            }
        }

        return releasedCount;
    }

    public static func TryReleasePrologueChecksOnSpawn(game: GameInstance) -> Void {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game) as QuestsSystem;
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(APConstants.GetTCPClientName()) as TCPClient;

        if !IsDefined(questSystem) || !IsDefined(tcpClient) {
            return;
        }

        let mode: Int32 = APNGPlusBridge.GetPrologueReleaseMode(questSystem);
        if mode < 1 {
            return;
        }

        let releasedCount: Int32 = APNGPlusBridge.ReleasePrologueChecks(questSystem, tcpClient, mode);
        if releasedCount > 0 {
            APLogger.LogInfo(s"NG+ bridge released \(releasedCount) prologue check(s) on spawn.");
        }
    }

    public static func IsPastPrologueForEnforcement(game: GameInstance) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game) as QuestsSystem;
        let mode: Int32 = APNGPlusBridge.GetPrologueReleaseMode(questSystem);
        return mode >= 1;
    }
}
