module Archipelago

public class APItemList {
    public let Items: array<ref<APItem>>;

    public func AddItem(itemID: String, amount: Int32) -> Void {
        APLogger.LogDebug(s"Adding Item to List \(itemID) amount: \(amount)");
        //If we already have this item, add to the amount
        if this.Contains(itemID){
            for extractedItem in this.Items {
                if StrCmp(extractedItem.itemID, itemID) == 0 {
                    extractedItem.AddItem(amount);
                }
            }
        } //If we dont, create a new instance of that item in the list
        else {
            let newItem: ref<APItem> = new APItem();
            newItem.itemID = itemID;
            newItem.AddItem(amount);
            ArrayPush(this.Items, newItem);
        }

    }

    public func GetItemByID(itemID: String) -> ref<APItem> {
        for extractedItem in this.Items {
            if StrCmp(extractedItem.itemID, itemID) == 0 {
                return extractedItem;
            }
        }
        return null;
    }

    public func Contains(itemID: String) -> Bool {
        for extractedItem in this.Items {
            if StrCmp(extractedItem.itemID, itemID) == 0{
                return true;
            }
        }
        return false;
    }
}

public class APItem {
    public let itemID: String;
    public let totalFromAP: Int32;

    public func AddItem(amount: Int32) -> Void {
        this.totalFromAP = this.totalFromAP + amount;
    }
}
