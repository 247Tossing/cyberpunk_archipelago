module Archipelago

// Pure data holder for Archipelago game state
// All business logic has been moved to APGameSystem
public class APGameState extends ScriptableService {
    // State flags
    public let diedFromDeathLink: Bool;
    public let skillPointsAsItems: Bool;
    public let enableDeathLink: Bool;
    public let restrictByMajorDistrict: Bool;

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
    // SyncData() call after a save reload silently aborted with "item list not available",
    // preventing already-owned district tokens from being re-applied and causing softlocks.
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

    public func SetRestrictByMajorDistrict(value: Bool) -> Bool {
        let changed: Bool = (this.restrictByMajorDistrict && !value) || (!this.restrictByMajorDistrict && value);
        this.restrictByMajorDistrict = value;
        return changed;
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

    public func HandlePlayerRespawn() -> Void {
        this.diedFromDeathLink = false;
    }
}
