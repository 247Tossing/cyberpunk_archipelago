module Archipelago

// Manages district unlock status and enforcement
// Separates district logic from teleportation mechanics
// Uses ScriptableSystem pattern for proper lifecycle management
public class APDistrictManager extends ScriptableSystem {
    private let districtEnforcer: ref<APDistrictEnforcer>;
    private let questHandler: ref<APQuestHandler>;

    public func OnAttach() -> Void {
        // Get references to other systems via container
        let container: ref<ScriptableSystemsContainer> = this.GetGameInstance().GetScriptableSystemsContainer();
        this.districtEnforcer = container.Get(n"Archipelago.APDistrictEnforcer") as APDistrictEnforcer;
        this.questHandler = container.Get(n"Archipelago.APQuestHandler") as APQuestHandler;

        APLogger.LogDebug("APDistrictManager initialized");
    }

    // Check if a district is unlocked 
    public func IsDistrictUnlocked(districtId: String) -> Bool {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        APLogger.LogDebug(s"IsDistrictUnlocked('\(districtId)'): APGameStateDefined=\(IsDefined(APGameState)), restrictByMajorDistrict=\(IsDefined(APGameState) && APGameState.restrictByMajorDistrict)");
        if !IsDefined(APGameState) || !APGameState.restrictByMajorDistrict {
            APLogger.LogDebug("District Restriction Disabled: All districts are considered unlocked");
            return true;
        }

        if !IsDefined(this.questHandler) {
            APLogger.LogDebug("APDistrictManager: Quest handler not initialized");
            return false;
        }
        if StrCmp(districtId, "unknown") == 0 {
            APLogger.LogDebug(s"IsDistrictUnlocked('\(districtId)'): 'unknown' district - treating as unlocked");
            return true;
        }
        let hasKey: Bool = this.questHandler.HasQuestKey(districtId);
        APLogger.LogDebug(s"IsDistrictUnlocked('\(districtId)'): HasQuestKey=\(hasKey)");
        return hasKey;
    }

    // Unlock a district
    public func UnlockDistrict(districtId: String) -> Void {
        APLogger.LogDebug(s"UnlockDistrict('\(districtId)') called - questHandlerDefined=\(IsDefined(this.questHandler))");
        if !IsDefined(this.questHandler) {
            APLogger.LogDebug("APDistrictManager: Quest handler not initialized");
            return;
        }

        // Only report success when the quest fact write actually succeeded - previously this logged
        // "District unlocked" unconditionally, which was misleading when SetQuestKey failed (e.g. the
        // quest system wasn't available yet), leaving the district silently still locked.
        if this.questHandler.SetQuestKey(districtId) {
            APLogger.LogInfo(s"District unlocked: \(districtId)");
        } else {
            APLogger.LogError(s"APDistrictManager: Failed to unlock district \(districtId) - quest system not available");
        }
    }

    // Handle district restriction (called when player enters locked district)
    public func HandleDistrictRestriction(districtString: String) -> Void {
        APLogger.LogDebug(s"HandleDistrictRestriction: rawDistrictString='\(districtString)' districtEnforcerDefined=\(IsDefined(this.districtEnforcer)) questHandlerDefined=\(IsDefined(this.questHandler))");
        if !IsDefined(this.districtEnforcer) {
            APLogger.LogDebug("APDistrictManager: District enforcer not initialized");
            return;
        }

        if !IsDefined(this.questHandler) {
            APLogger.LogDebug("APDistrictManager: Quest handler not initialized");
            return;
        }

        // Don't enforce during lifepath intro
        let passedPrologue: Bool = this.questHandler.IsPassedPrologue();
        APLogger.LogDebug(s"HandleDistrictRestriction: IsPassedPrologue=\(passedPrologue)");
        if !passedPrologue {
            return;
        }

        // Don't teleport while a post-spawn/connect item resync is still draining - the quest facts
        // HasQuestKey reads below may not yet reflect district tokens the player already owns (see
        // APGameState.itemResyncPending / TCPClient.ArmItemResyncPending). This is what caused the
        // softlock: SyncData ran with an empty/incomplete item list right after a save reload, and
        // entering a district before the AP item backlog finished replaying got the player kicked
        // out of a district they actually owned the token for.
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if IsDefined(APGameState) && APGameState.IsItemResyncPending() {
            APLogger.LogInfo("APDistrictManager: Deferring district enforcement - item resync still in progress");
            return;
        }

        // Get the major district enum from the game's district string
        let district: APDistrict = this.districtEnforcer.GetMajorDistrict(districtString);
        let districtId: String = this.districtEnforcer.ParseEnumToDistrictID(district);
        APLogger.LogDebug(s"HandleDistrictRestriction: rawDistrictString='\(districtString)' -> APDistrict=\(district) -> districtId='\(districtId)'");

        // If district is unlocked, no need to teleport
        let unlocked: Bool = this.IsDistrictUnlocked(districtId);
        APLogger.LogDebug(s"HandleDistrictRestriction: IsDistrictUnlocked('\(districtId)')=\(unlocked)");
        if unlocked {
            return;
        }

        APLogger.LogInfo(s"District locked. Requires Access Token");
        APLogger.LogDebug(s"Locked district: \(districtId)");
        // District is locked - teleport player to nearest safe point
        this.TeleportToSafeZone();
    }

    // Teleport player to nearest safe zone in an unlocked district
    private func TeleportToSafeZone() -> Void {
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();

        if !IsDefined(player) {
            APLogger.LogDebug("APDistrictManager: Cannot teleport - player not available");
            return;
        }

        let currentPos: Vector4 = player.GetWorldPosition();
        APLogger.LogDebug(s"TeleportToSafeZone: currentPos=(\(currentPos.X), \(currentPos.Y), \(currentPos.Z))");
        let nearestSafePoint: Vector4 = this.districtEnforcer.GetNearestSafePoint(currentPos);
        APLogger.LogDebug(s"TeleportToSafeZone: nearestSafePoint=(\(nearestSafePoint.X), \(nearestSafePoint.Y), \(nearestSafePoint.Z))");

        // Set default rotation
        let targetRotation: EulerAngles = EulerAngles();
        targetRotation.Pitch = 0.0;
        targetRotation.Roll = 0.0;
        targetRotation.Yaw = 180.0;

        let teleportFacility: ref<TeleportationFacility> = GameInstance.GetTeleportationFacility(this.GetGameInstance());
        if IsDefined(teleportFacility) {
            teleportFacility.Teleport(player, nearestSafePoint, targetRotation);
            APLogger.LogInfo("Player teleported to unlocked district");
        } else {
            APLogger.LogDebug("APDistrictManager: Cannot teleport - teleportation facility not available");
        }
    }

    // Initialize Watson as unlocked (default starting district)
    public func InitializeDefaultDistrict() -> Void {
        this.UnlockDistrict(APConstants.GetWatsonAccessToken());
    }
}
