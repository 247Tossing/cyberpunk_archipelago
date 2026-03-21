module Archipelago

public class APLogger {

    public static func LogError(message: String) -> Void {
        FTLogError(s"[Archipelago] \(message)");
    }

    public static func LogWarning(message: String) -> Void {
        FTLogWarning( s"[Archipelago] \(message)");
    }

    public static func LogInfo(message: String) -> Void {
        FTLog(s"[Archipelago] \(message)");
    }

    // Verbose debug log — only outputs when quest fact "ap_enable_debug_logs" is set to 1.
    // Enable via CET console: Game.GetQuestsSystem():SetFact("ap_enable_debug_logs", 1)
    public static func LogDebug(message: String) -> Void {
        let verboseLogging: Bool = false; // This is meant to be set manually - False by default
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(GetGameInstance());
        if (IsDefined(questSystem) && questSystem.GetFact(APConstants.GetDebugLogFact()) >= 1) || verboseLogging {
            FTLog(s"[Archipelago][DEBUG] \(message)");
        }
    }
}

