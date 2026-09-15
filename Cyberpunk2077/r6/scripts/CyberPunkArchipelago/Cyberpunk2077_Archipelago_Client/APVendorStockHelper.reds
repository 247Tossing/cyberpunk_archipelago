module Archipelago

private func ResolveVendorCheckLocationId(item: wref<UIInventoryItem>) -> String {
    if !IsDefined(item) {
        return "";
    }

    let itemRecord = item.GetItemRecord();
    if !IsDefined(itemRecord) {
        return "";
    }

    let itemTags = itemRecord.Tags();
    let tagIndex: Int32 = 0;
    while tagIndex < ArraySize(itemTags) {
        let tagString: String = s"\(itemTags[tagIndex])";
        if StrContains(tagString, "VendorCheck_") {
            return tagString;
        }
        tagIndex += 1;
    }

    return "";
}

private func FindVendorSanityItem(locationId: String) -> ref<APVendorItem> {
    if StrLen(locationId) == 0 {
        return null;
    }

    let gameState = GameInstance.GetScriptableServiceContainer().GetService(APConstants.GetAPGameStateName()) as APGameState;
    if !IsDefined(gameState) || !gameState.vendorSanityEnabled {
        return null;
    }

    let rowIndex: Int32 = 0;
    while rowIndex < ArraySize(gameState.vendorSanityItems) {
        let entry: ref<APVendorItem> = gameState.vendorSanityItems[rowIndex];
        if IsDefined(entry) {
            let locationCheckId: String = s"VendorCheck_\(entry.vendorName)_\(ToString(entry.slotIndex))";
            if StrCmp(locationCheckId, locationId) == 0 {
                return entry;
            }
        }
        rowIndex += 1;
    }

    return null;
}

@wrapMethod(UIInventoryItem)
public final func GetName() -> String {
    let fallbackName: String = wrappedMethod();
    let locationId: String = ResolveVendorCheckLocationId(this);
    let entry: ref<APVendorItem> = FindVendorSanityItem(locationId);

    if IsDefined(entry) && StrLen(entry.itemName) > 0 {
        return entry.itemName;
    }

    return fallbackName;
}

@wrapMethod(UIInventoryItem)
public final func GetDescription() -> String {
    let fallbackDescription: String = wrappedMethod();
    let locationId: String = ResolveVendorCheckLocationId(this);
    let entry: ref<APVendorItem> = FindVendorSanityItem(locationId);

    if IsDefined(entry) && StrLen(entry.recipientName) > 0 {
        return s"For: \(entry.recipientName)";
    }

    return fallbackDescription;
}