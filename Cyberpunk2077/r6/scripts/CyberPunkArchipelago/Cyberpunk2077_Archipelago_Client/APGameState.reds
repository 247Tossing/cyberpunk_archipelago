module Archipelago

// Pure data holder for Archipelago game state
// All business logic has been moved to APGameSystem
public class APGameState extends ScriptableService {
    // State flags
    public let diedFromDeathLink: Bool;
    public let skillPointsAsItems: Bool;
    public let enableDeathLink: Bool;
    public let restrictByMajorDistrict: Bool;
    public let restrictBySubDistrict: Bool;
    public let districtTokenGatedMajorMask: Int32;
    public let districtRestrictionConfigInitialized: Bool;
    public let vendorSanityEnabled: Bool;
    public let vendorSanityStockLine: String;
    public let vendorSanityItems: array<ref<APVendorItem>>;
    public let vendorSanityConfigInitialized: Bool;

    // Completion goal settings (synced from APWorld options via slot_data).
    // completionGoal values match APConstants.GetCompletionGoal*; gigGoalIds is
    // only populated for the Fixers-Only goal and lists the internal quest IDs
    // of every gig this seed requires.
    public let completionGoal: Int32;
    public let gigGoalManifestLine: String;
    public let gigGoalIds: array<String>;
    public let goalConfigInitialized: Bool;

    // Weapon restriction settings (synced from APWorld options via slot_data)
    // weaponRestrictionType: 0 = none, 1 = cannotEquip (hard ban), 2 = requireMultiworldItem (pass-gated)
    public let weaponRestrictionType: Int32;
    public let weaponRestrictPistol: Bool;
    public let weaponRestrictMelee: Bool;
    public let weaponRestrictRifle: Bool;
    public let weaponRestrictSniper: Bool;
    public let weaponRestrictLmg: Bool;
    public let weaponRestrictShotgun: Bool;
    public let weaponRestrictSmg: Bool;
    public let weaponRestrictionConfigInitialized: Bool;

    // Item tracking
    public let items: ref<APItemList>;

    // Phone notification system
    public let phoneSystem: ref<APPhoneSystem>;

    // Track total NetworkItems received from Python (not unique item types)
    // This matches Python's len(received_items) counting for SYNC_COMPLETE
    public let totalNetworkItemsReceived: Int32;

    // True while a post-spawn/connect item resync is in flight (TCPClient is still draining the
    // native item queue after a save load or fresh connect). District enforcement should not
    // teleport the player while this is set, since the quest facts it reads may not reflect
    // already-owned tokens yet - see APDistrictManager.HandleDistrictRestriction.
    public let itemResyncPending: Bool;

    // ScriptableService's lifecycle callback is OnLoad (runs once when the game starts, independent
    // of save load/unload) - NOT OnAttach, which is a ScriptableSystem callback for save-bound
    // singletons. Using OnAttach here meant this never ran, so `items` stayed undefined and every
    // SyncData() call after a save reload silently aborted, preventing already-owned district
    // tokens from being re-applied and causing softlocks.
    private func OnLoad() -> Void {
        if !IsDefined(this.items) {
            this.items = new APItemList();
        }
        APLogger.LogInfo("Cyberpunk 2077 Archipelago Game State Ready");
    }

    public func GetPhoneSystem() -> ref<APPhoneSystem> {
        if !IsDefined(this.phoneSystem) {
            APLogger.LogDebug("APGameState: Lazy-creating APPhoneSystem");
            this.phoneSystem = new APPhoneSystem();
            this.phoneSystem.Initialize();
        }
        return this.phoneSystem;
    }

    // ===== SIMPLE GETTERS/SETTERS ONLY =====

    // Lazy-initializes `items` as a defensive fallback in case this is ever called before OnLoad
    // has run, so callers never have to null-check the result.
    public func GetItems() -> ref<APItemList> {
        if !IsDefined(this.items) {
            APLogger.LogDebug("APGameState: Lazy-creating item list");
            this.items = new APItemList();
        }
        return this.items;
    }

    public func IsItemResyncPending() -> Bool {
        return this.itemResyncPending;
    }

    public func SetItemResyncPending(value: Bool) -> Void {
        this.itemResyncPending = value;
    }

    public func DiedFromDeathLink() -> Void {
        this.diedFromDeathLink = true;
    }

    public func SetEnableDeathLink(value: Bool) -> Bool {
        let changed: Bool = (this.enableDeathLink && !value) || (!this.enableDeathLink && value);
        this.enableDeathLink = value;
        return changed;
    }

    public func SetRestrictByMajorDistrict(value: Bool) -> Void {
        this.restrictByMajorDistrict = value;
    }

    public func SetDistrictRestrictionConfig(restrictMajor: Bool, restrictSub: Bool, gatedMajorMask: Int32) -> Bool {
        let changed: Bool = !this.districtRestrictionConfigInitialized
            || (this.restrictByMajorDistrict && !restrictMajor)
            || (!this.restrictByMajorDistrict && restrictMajor)
            || (this.restrictBySubDistrict && !restrictSub)
            || (!this.restrictBySubDistrict && restrictSub)
            || this.districtTokenGatedMajorMask < gatedMajorMask
            || this.districtTokenGatedMajorMask > gatedMajorMask;

        this.restrictByMajorDistrict = restrictMajor;
        this.restrictBySubDistrict = restrictSub;
        this.districtTokenGatedMajorMask = gatedMajorMask;
        this.districtRestrictionConfigInitialized = true;
        return changed;
    }

    public func SetVendorSanityData(enabled: Bool, stockLine: String) -> Bool {
        let changed: Bool = !this.vendorSanityConfigInitialized
            || (this.vendorSanityEnabled && !enabled)
            || (!this.vendorSanityEnabled && enabled)
            || StrCmp(this.vendorSanityStockLine, stockLine) != 0;

        this.vendorSanityEnabled = enabled;
        this.vendorSanityStockLine = stockLine;
        this.vendorSanityItems = APVendorItem.ParseStockLine(stockLine);
        this.vendorSanityConfigInitialized = true;
        if changed {
            this.LogVendorSanitySlotDataDebug();
        }
        return changed;
    }

    public func SetGoalConfig(goal: Int32, gigManifestLine: String) -> Bool {
        let changed: Bool = !this.goalConfigInitialized
            || this.completionGoal < goal
            || this.completionGoal > goal
            || StrCmp(this.gigGoalManifestLine, gigManifestLine) != 0;

        this.completionGoal = goal;
        this.gigGoalManifestLine = gigManifestLine;
        this.gigGoalIds = APGameState.ParseGigManifest(gigManifestLine);
        this.goalConfigInitialized = true;
        return changed;
    }

    public func IsFixersOnlyGoal() -> Bool {
        return this.goalConfigInitialized
            && this.completionGoal == APConstants.GetCompletionGoalAllFixerGigs();
    }

    // Splits the comma-separated gig_goal_manifest slot_data line into quest IDs.
    private static func ParseGigManifest(manifestLine: String) -> array<String> {
        let gigIds: array<String>;
        if StrLen(manifestLine) == 0 {
            return gigIds;
        }

        let parts: array<String> = StrSplit(manifestLine, ",");
        for part in parts {
            if StrLen(part) > 0 {
                ArrayPush(gigIds, part);
            }
        }
        return gigIds;
    }

    public func SetWeaponRestrictionConfig(
        restrictionType: Int32,
        restrictPistol: Bool,
        restrictMelee: Bool,
        restrictRifle: Bool,
        restrictSniper: Bool,
        restrictLmg: Bool,
        restrictShotgun: Bool,
        restrictSmg: Bool
    ) -> Bool {
        let changed: Bool = !this.weaponRestrictionConfigInitialized
            || this.weaponRestrictionType < restrictionType
            || this.weaponRestrictionType > restrictionType
            || (this.weaponRestrictPistol && !restrictPistol)
            || (!this.weaponRestrictPistol && restrictPistol)
            || (this.weaponRestrictMelee && !restrictMelee)
            || (!this.weaponRestrictMelee && restrictMelee)
            || (this.weaponRestrictRifle && !restrictRifle)
            || (!this.weaponRestrictRifle && restrictRifle)
            || (this.weaponRestrictSniper && !restrictSniper)
            || (!this.weaponRestrictSniper && restrictSniper)
            || (this.weaponRestrictLmg && !restrictLmg)
            || (!this.weaponRestrictLmg && restrictLmg)
            || (this.weaponRestrictShotgun && !restrictShotgun)
            || (!this.weaponRestrictShotgun && restrictShotgun)
            || (this.weaponRestrictSmg && !restrictSmg)
            || (!this.weaponRestrictSmg && restrictSmg);

        this.weaponRestrictionType = restrictionType;
        this.weaponRestrictPistol = restrictPistol;
        this.weaponRestrictMelee = restrictMelee;
        this.weaponRestrictRifle = restrictRifle;
        this.weaponRestrictSniper = restrictSniper;
        this.weaponRestrictLmg = restrictLmg;
        this.weaponRestrictShotgun = restrictShotgun;
        this.weaponRestrictSmg = restrictSmg;
        this.weaponRestrictionConfigInitialized = true;
        return changed;
    }

    public func IsDistrictTokenGated(districtId: String) -> Bool {
        if !this.restrictByMajorDistrict {
            return false;
        }

        if StrCmp(districtId, APConstants.GetWestbrookAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetWestbrookGateMask());
        }
        if StrCmp(districtId, APConstants.GetCityCenterAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetCityCenterGateMask());
        }
        if StrCmp(districtId, APConstants.GetHeywoodAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetHeywoodGateMask());
        }
        if StrCmp(districtId, APConstants.GetSantoDomingoAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetSantoDomingoGateMask());
        }
        if StrCmp(districtId, APConstants.GetPacificaAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetPacificaGateMask());
        }
        if StrCmp(districtId, APConstants.GetBadlandsAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetBadlandsGateMask());
        }
        if StrCmp(districtId, APConstants.GetDogtownAccessToken()) == 0 {
            return this.MaskHasBit(APConstants.GetDogtownGateMask());
        }
        return false;
    }

    public func GetGatedDistrictSummary() -> String {
        if !this.restrictByMajorDistrict {
            return "none";
        }

        let summary: String = "";
        if this.IsDistrictTokenGated(APConstants.GetWestbrookAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "westbrook");
        }
        if this.IsDistrictTokenGated(APConstants.GetCityCenterAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "city_center");
        }
        if this.IsDistrictTokenGated(APConstants.GetHeywoodAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "heywood");
        }
        if this.IsDistrictTokenGated(APConstants.GetSantoDomingoAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "santo_domingo");
        }
        if this.IsDistrictTokenGated(APConstants.GetPacificaAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "pacifica");
        }
        if this.IsDistrictTokenGated(APConstants.GetBadlandsAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "badlands");
        }
        if this.IsDistrictTokenGated(APConstants.GetDogtownAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "dogtown");
        }

        if StrLen(summary) == 0 {
            return "none";
        }
        return summary;
    }

    public func GetAutoOpenDistrictSummary() -> String {
        if !this.restrictByMajorDistrict {
            return "all";
        }

        let summary: String = "";
        if !this.IsDistrictTokenGated(APConstants.GetWestbrookAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "westbrook");
        }
        if !this.IsDistrictTokenGated(APConstants.GetCityCenterAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "city_center");
        }
        if !this.IsDistrictTokenGated(APConstants.GetHeywoodAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "heywood");
        }
        if !this.IsDistrictTokenGated(APConstants.GetSantoDomingoAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "santo_domingo");
        }
        if !this.IsDistrictTokenGated(APConstants.GetPacificaAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "pacifica");
        }
        if !this.IsDistrictTokenGated(APConstants.GetBadlandsAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "badlands");
        }
        if !this.IsDistrictTokenGated(APConstants.GetDogtownAccessToken()) {
            summary = this.AppendDistrictSummary(summary, "dogtown");
        }

        if StrLen(summary) == 0 {
            return "none";
        }
        return summary;
    }

    private func MaskHasBit(bit: Int32) -> Bool {
        let value: Int32 = this.districtTokenGatedMajorMask;
        while value >= bit * 2 {
            value -= bit * 2;
        }
        return value >= bit;
    }

    private func AppendDistrictSummary(summary: String, district: String) -> String {
        if StrLen(summary) == 0 {
            return district;
        }
        return s"\(summary),\(district)";
    }

    // slot_data vendor_sanity / vendor_sanity_stock — log what the client received and how it maps to checks
    private func LogVendorSanitySlotDataDebug() -> Void {
        APLogger.LogDebug(
            s"APGameState: Vendor sanity (slot_data) — enabled=\(this.vendorSanityEnabled), raw_vendor_sanity_stock=\"\(this.vendorSanityStockLine)\""
        );

        if ArraySize(this.vendorSanityItems) == 0 {
            APLogger.LogDebug("APGameState: Vendor sanity — no parsed stock rows (empty line, option off, or malformed Vendor:Index:Item:Recipient records)");
            return;
        }

        let rowIndex: Int32 = 0;
        while rowIndex < ArraySize(this.vendorSanityItems) {
            let entry: ref<APVendorItem> = this.vendorSanityItems[rowIndex];
            if IsDefined(entry) {
                let locationCheckId: String = s"VendorCheck_\(entry.vendorName)_\(ToString(entry.slotIndex))";
                let wireId: Int64 = APNativeMappings.ResolveLocationAddress(locationCheckId);
                if wireId >= 0l {
                    APLogger.LogDebug(
                        s"APGameState: Vendor location assignment — check=\(locationCheckId), wire_id=\(ToString(wireId)), multiworld_item=\"\(entry.itemName)\", recipient=\"\(entry.recipientName)\", vendor_key=\"\(entry.vendorName)\", slot_index=\(ToString(entry.slotIndex))"
                    );
                } else {
                    APLogger.LogDebug(
                        s"APGameState: Vendor location assignment — check=\(locationCheckId) has NO mapping (wire_id=-1); stock row vendor=\"\(entry.vendorName)\", slot_index=\(ToString(entry.slotIndex)), item=\"\(entry.itemName)\", recipient=\"\(entry.recipientName)\""
                    );
                }
            }
            rowIndex += 1;
        }
    }

    // Returns true if the given locationId (e.g. "VendorCheck_Victor_1") is part of this run's
    // vendor_sanity_stock. Items absent from the stock were either from a disabled category or
    // were never added, and should be hidden from vendor inventories.
    public func IsVendorCheckInRun(locationId: String) -> Bool {
        let i: Int32 = 0;
        while i < ArraySize(this.vendorSanityItems) {
            let entry: ref<APVendorItem> = this.vendorSanityItems[i];
            if IsDefined(entry) {
                let entryId: String = s"VendorCheck_\(entry.vendorName)_\(ToString(entry.slotIndex))";
                if StrCmp(entryId, locationId) == 0 {
                    return true;
                }
            }
            i += 1;
        }
        return false;
    }

    public func ShouldShowVendorCheckInInventory(locationId: String) -> Bool {
        if !this.vendorSanityConfigInitialized {
            return true;
        }
        if !this.vendorSanityEnabled {
            return false;
        }
        return this.IsVendorCheckInRun(locationId);
    }

    public func HandlePlayerRespawn() -> Void {
        this.diedFromDeathLink = false;
    }
}
