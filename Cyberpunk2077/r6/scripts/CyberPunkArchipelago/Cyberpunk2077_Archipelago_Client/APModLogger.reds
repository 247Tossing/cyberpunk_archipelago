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
}

