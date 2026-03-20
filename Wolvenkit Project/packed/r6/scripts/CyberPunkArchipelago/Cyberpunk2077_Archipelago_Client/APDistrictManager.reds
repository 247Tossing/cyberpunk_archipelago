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

        APLogger.LogInfo("APDistrictManager initialized");
    }

    // Check if a district is unlocked 
    public func IsDistrictUnlocked(districtId: String) -> Bool {
        if !IsDefined(this.questHandler) {
            APLogger.LogWarning("APDistrictManager: Quest handler not initialized");
            return false;
        }
        if StrCmp(districtId, "unknown") == 0 {
            return true;
        }
        return this.questHandler.HasQuestKey(districtId);
    }

    // Unlock a district
    public func UnlockDistrict(districtId: String) -> Void {
        if !IsDefined(this.questHandler) {
            APLogger.LogWarning("APDistrictManager: Quest handler not initialized");
            return;
        }
        this.questHandler.SetQuestKey(districtId);
        APLogger.LogInfo(s"District unlocked: \(districtId)");
    }

    // Handle district restriction (called when player enters locked district)
    public func HandleDistrictRestriction(districtString: String) -> Void {
        if !IsDefined(this.districtEnforcer) {
            APLogger.LogWarning("APDistrictManager: District enforcer not initialized");
            return;
        }

        if !IsDefined(this.questHandler) {
            APLogger.LogWarning("APDistrictManager: Quest handler not initialized");
            return;
        }

        // Don't enforce during lifepath intro
        if !this.questHandler.IsLifepathIntroComplete() {
            return;
        }

        // Get the major district enum from the game's district string
        let district: APDistrict = this.districtEnforcer.GetMajorDistrict(districtString);
        let districtId: String = this.districtEnforcer.ParseEnumToDistrictID(district);

        // If district is unlocked, no need to teleport
        if this.IsDistrictUnlocked(districtId) {
            return;
        }

        APLogger.LogInfo(s"District \(districtId) locked. Requires Access Token");
        // District is locked - teleport player to nearest safe point
        this.TeleportToSafeZone();
    }

    // Teleport player to nearest safe zone in an unlocked district
    private func TeleportToSafeZone() -> Void {
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();

        if !IsDefined(player) {
            APLogger.LogWarning("APDistrictManager: Cannot teleport - player not available");
            return;
        }

        let currentPos: Vector4 = player.GetWorldPosition();
        let nearestSafePoint: Vector4 = this.districtEnforcer.GetNearestSafePoint(currentPos);

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
            APLogger.LogWarning("APDistrictManager: Cannot teleport - teleportation facility not available");
        }
    }

    // Initialize Watson as unlocked (default starting district)
    public func InitializeDefaultDistrict() -> Void {
        this.UnlockDistrict(APConstants.GetWatsonAccessToken());
    }
}
