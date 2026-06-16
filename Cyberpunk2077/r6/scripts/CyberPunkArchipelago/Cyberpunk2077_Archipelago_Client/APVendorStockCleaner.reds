module Archipelago

// Removes already-checked and disabled-category vendor items from a vendor's live
// inventory each time the vendor UI opens. This handles the case where vendor stock
// refreshes on the 24-hour in-game timer and restores items the player already checked.
//
// "Already checked" is detected via the ap_VendorCheck_* quest facts written by
// APVendorTransactionReader on purchase — no additional state is introduced.
//
// "Disabled category" is detected by checking whether the locationId appears in the
// vendorSanityItems list (vendor_sanity_stock from slot_data). Items from vendor
// categories that were not enabled for this seed are absent from that list and will
// be removed from the live inventory so they never appear in the vendor UI.

@addMethod(FullscreenVendorGameController)
private func APCleanCheckedVendorItems() -> Void {
    let vendorInstance: wref<GameObject> = this.m_VendorDataManager.GetVendorInstance();
    if !IsDefined(vendorInstance) {
        APLogger.LogDebug("Vendor UI: FullscreenVendorGameController.Init — GetVendorInstance() returned null");
        return;
    }

    let game: GameInstance = vendorInstance.GetGame();
    let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(game) as QuestsSystem;
    let ts: ref<TransactionSystem> = GameInstance.GetTransactionSystem(game);

    if !IsDefined(questSystem) || !IsDefined(ts) {
        return;
    }

    let entityIdStr: String = ToString(vendorInstance.GetEntityID());
    let npcRecordStr: String = "n/a";
    let asPuppet: wref<ScriptedPuppet> = vendorInstance as ScriptedPuppet;
    if IsDefined(asPuppet) {
        npcRecordStr = TDBID.ToStringDEBUG(asPuppet.GetRecordID());
    }
    APLogger.LogDebug(s"Vendor UI: vendor npcRecord=\(npcRecordStr), entityId=\(entityIdStr)");

    let isConnected: Bool = AP_IsConnected();
    let gameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;

    let locationIds: array<String> = APArchipelagoIdMappings.GetAllLocationIds();
    let vendorCheckItemsInStock: Int32 = 0;
    let i: Int32 = 0;
    while i < ArraySize(locationIds) {
        let locationId: String = locationIds[i];
        if StrContains(locationId, "VendorCheck_") {
            let itemTDBID: TweakDBID = TDBID.Create(s"Items.\(locationId)");
            let itemID: ItemID = ItemID.FromTDBID(itemTDBID);
            let itemData: wref<gameItemData> = ts.GetItemData(vendorInstance, itemID);
            if IsDefined(itemData) {
                vendorCheckItemsInStock += 1;
            }

            let shouldRemove: Bool = false;

            // Remove if already purchased (fact written at buy time)
            let factName: CName = StringToName(s"ap_\(locationId)");
            if questSystem.GetFact(factName) >= 1 {
                shouldRemove = true;
            }

            // Remove if connected and this check is not part of the active run's vendor stock
            // (covers disabled sub-categories and checks not assigned to any vendor this seed)
            if !shouldRemove && isConnected && IsDefined(gameState) && gameState.vendorSanityEnabled {
                if !gameState.IsVendorCheckInRun(locationId) {
                    shouldRemove = true;
                }
            }

            if shouldRemove {
                if IsDefined(itemData) {
                    ts.RemoveItem(vendorInstance, itemID, 1);
                    APLogger.LogDebug(s"Removed vendor item from stock: \(locationId)");
                }
            }
        }
        i += 1;
    }

    if vendorCheckItemsInStock > 0 {
        APLogger.LogDebug(s"Vendor UI: detected \(vendorCheckItemsInStock) VendorCheck_* line(s) in vendor live inventory (at open, before removals)");
    } else {
        APLogger.LogDebug("Vendor UI: no VendorCheck_* lines detected in vendor live inventory (at open, before removals)");
    }
}

@wrapMethod(FullscreenVendorGameController)
private final func Init() -> Void {
    wrappedMethod();
    this.APCleanCheckedVendorItems();
}
