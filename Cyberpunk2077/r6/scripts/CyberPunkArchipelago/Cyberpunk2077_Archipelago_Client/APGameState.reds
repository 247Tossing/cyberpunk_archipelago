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

    // Weapon restriction settings (synced from APWorld options via SYNC_CONFIG)
    // weaponRestrictionType: 0 = none, 1 = cannotEquip (hard ban), 2 = requireMultiworldItem (pass-gated)
    public let weaponRestrictionType: Int32;
    public let weaponRestrictPistol: Bool;
    public let weaponRestrictMelee: Bool;
    public let weaponRestrictRifle: Bool;
    public let weaponRestrictSniper: Bool;
    public let weaponRestrictLmg: Bool;
    public let weaponRestrictShotgun: Bool;
    public let weaponRestrictSmg: Bool;

    // Item tracking
    public let items: ref<APItemList>;

    // Phone notification system
    public let phoneSystem: ref<APPhoneSystem>;

    // Track total NetworkItems received from Python (not unique item types)
    // This matches Python's len(received_items) counting for SYNC_COMPLETE
    public let totalNetworkItemsReceived: Int32;

    private func OnAttach() -> Void {
        this.items = new APItemList();
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

    public func GetItems() -> ref<APItemList> {
        return this.items;
    }

    public func DiedFromDeathLink() -> Void {
        this.diedFromDeathLink = true;
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
        let changed: Bool = (this.vendorSanityEnabled && !enabled)
            || (!this.vendorSanityEnabled && enabled)
            || StrCmp(this.vendorSanityStockLine, stockLine) != 0;

        this.vendorSanityEnabled = enabled;
        this.vendorSanityStockLine = stockLine;
        this.vendorSanityItems = APVendorItem.ParseStockLine(stockLine);
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

    public func HandlePlayerRespawn() -> Void {
        this.diedFromDeathLink = false;
    }
}
