module Archipelago

// Parsed representation of one vendor stock record from slot_data.
// Wire format: VendorName:Index:ItemName:Recipient
public class APVendorItem {
    public let vendorName: String;
    public let slotIndex: Int32;
    public let itemName: String;
    public let recipientName: String;

    public static func ParseStockLine(stockLine: String) -> array<ref<APVendorItem>> {
        let items: array<ref<APVendorItem>>;
        if StrLen(stockLine) == 0 {
            return items;
        }

        let records: array<String> = StrSplit(stockLine, ",");
        let recordIndex: Int32 = 0;

        while recordIndex < ArraySize(records) {
            let record: String = records[recordIndex];
            if StrLen(record) > 0 {
                let fields: array<String> = StrSplit(record, ":");
                if ArraySize(fields) >= 4 {
                    let item: ref<APVendorItem> = new APVendorItem();
                    item.vendorName = fields[0];
                    item.slotIndex = StringToInt(fields[1]);
                    item.itemName = fields[2];
                    item.recipientName = fields[3];
                    ArrayPush(items, item);
                }
            }

            recordIndex += 1;
        }

        return items;
    }
}
