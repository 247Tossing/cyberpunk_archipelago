module Archipelago

@wrapMethod(VendorDataManager)
public final func BuyItemFromVendor(item: wref<gameItemData>, quantity: Int32, opt requestId: Int32) -> Void {
    let locationId: String = "";

    if IsDefined(item) {
        let itemID = item.GetID();
        let itemTDBID = itemID.GetTDBID();
        let itemRecord = TweakDBInterface.GetItemRecord(itemTDBID);
        if IsDefined(itemRecord) {
            let itemTags = itemRecord.Tags();
            let tagIndex: Int32 = 0;
            while tagIndex < ArraySize(itemTags) {
                let tagString: String = s"\(itemTags[tagIndex])";
                if StrContains(tagString, "VendorCheck_") {
                    locationId = tagString;
                    break;
                }
                tagIndex += 1;
            }
        }
    }

    if StrLen(locationId) > 0 {
        APLogger.LogDebug(s"Buying VendorCheck item:\(locationId)");
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(GetGameInstance()) as QuestsSystem;
        let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(APConstants.GetTCPClientName()) as TCPClient;
        APQuestLocationLookup.SendLocationCheck(questSystem, tcpService, locationId);

        wrappedMethod(item, quantity, requestId);
    }
    else {
        wrappedMethod(item, quantity, requestId);
    }
}