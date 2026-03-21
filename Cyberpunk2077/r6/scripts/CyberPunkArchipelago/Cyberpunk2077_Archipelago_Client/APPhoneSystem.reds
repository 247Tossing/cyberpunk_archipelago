module Archipelago
import PhoneExtension.Classes.*
import PhoneExtension.System.*
import PhoneExtension.DataStructures.*

// ===== MESSAGE DATA =====

public class APPhoneMessage extends IScriptable {
    public let senderName: String;
    public let itemDisplayName: String;
}

// ===== CONTACT (PhoneExtension listener) =====

public class APPhoneContact extends PhoneEventsListener {

    private let messages: array<ref<APPhoneMessage>>;
    private let lastPreview: String;

    public func GetContactHash() -> Int32 {
        return APConstants.GetArchipelagoContactHash();
    }

    public func GetContactData(isText: Bool) -> ref<ContactData> {
        let contactData: ref<ContactData> = new ContactData();
        contactData.hash = this.GetContactHash();
        contactData.localizedName = s"Archipelago";
        contactData.contactId = s"ArchipelagoContact";
        contactData.id = s"APCNTCT";
        contactData.avatarID = t"PhoneAvatars.Avatar_Unknown";
        contactData.questRelated = false;
        contactData.isCallable = false;
        if isText {
            contactData.type = MessengerContactType.SingleThread;
            if StrLen(this.lastPreview) > 0 {
                contactData.lastMesssagePreview = this.lastPreview;
            } else {
                contactData.lastMesssagePreview = s"Archipelago Multiworld";
            };
        } else {
            contactData.type = MessengerContactType.Contact;
        };
        contactData.messagesCount = ArraySize(this.messages);
        contactData.hasMessages = ArraySize(this.messages) > 0;
        contactData.playerIsLastSender = false;

        return contactData;
    }

    public func ShowDialog(messengerController: wref<MessengerDialogViewController>) -> Bool {
        APLogger.LogDebug(s"APPhoneContact: ShowDialog called, message count: \(ArraySize(this.messages))");
        if ArraySize(this.messages) == 0 {
            messengerController.PushMessageCustom(
                s"No items received yet.",
                MessageViewType.Received,
                s"Archipelago",
                false
            );
            return true;
        }

        for msg in this.messages {
            APLogger.LogDebug(s"APPhoneContact: Pushing message - \(msg.senderName): \(msg.itemDisplayName)");
            messengerController.PushMessageCustom(
                s"\(msg.senderName) sent you \(msg.itemDisplayName)",
                MessageViewType.Received,
                msg.senderName,
                false
            );
        }

        return true;
    }

    public func AddMessage(senderName: String, itemDisplayName: String) -> Void {
        let msg: ref<APPhoneMessage> = new APPhoneMessage();
        msg.senderName = senderName;
        msg.itemDisplayName = itemDisplayName;
        ArrayPush(this.messages, msg);
        this.lastPreview = s"\(senderName): \(itemDisplayName)";
    }

    public func GetMessageCount() -> Int32 {
        return ArraySize(this.messages);
    }
}

// ===== COORDINATOR =====
// Owns the contact listener and exposes methods for registration and notifications.
//
// Usage:
//   Initialization (APGameState.OnAttach):
//     this.phoneSystem = new APPhoneSystem();
//     this.phoneSystem.Initialize();
//
//   Registration (OnMakePlayerVisibleAfterSpawn, every spawn):
//     APGameState.phoneSystem.RegisterContact(player);
//
//   Item notification (APGameSystem, when ITEM_RECEIVED arrives):
//     APGameState.phoneSystem.SendItemNotification(player, senderName, itemDisplayName);

public class APPhoneSystem extends IScriptable {

    private let contact: ref<APPhoneContact>;

    public func Initialize() -> Void {
        this.contact = new APPhoneContact();
        APLogger.LogDebug("APPhoneSystem: Initialized, contact created");
    }

    // Register the Archipelago contact with the phone UI.
    // Must be called every spawn (PhoneExtensionSystem resets on respawn).
    public func RegisterContact(player: ref<GameObject>) -> Void {
        if !IsDefined(player) {
            APLogger.LogDebug("APPhoneSystem: Cannot register contact, player is null");
            return;
        }
        let phoneSystem: ref<PhoneExtensionSystem> = PhoneExtensionSystem.GetInstance(player);
        if !IsDefined(phoneSystem) {
            APLogger.LogDebug("APPhoneSystem: PhoneExtensionSystem not available");
            return;
        }
        phoneSystem.Register(this.contact);
        APLogger.LogDebug("APPhoneSystem: Archipelago contact registered");
    }

    // Add a message to the chat thread and push a HUD SMS notification.
    // If player is null (not yet spawned), the message is queued but no HUD notification fires.
    public func SendItemNotification(player: ref<GameObject>, senderName: String, itemDisplayName: String) -> Void {
        APLogger.LogDebug(s"APPhoneSystem: SendItemNotification called - sender: \(senderName), item: \(itemDisplayName)");
        if !IsDefined(this.contact) {
            APLogger.LogDebug("APPhoneSystem: Contact not initialized");
            return;
        }

        this.contact.AddMessage(senderName, itemDisplayName);
        APLogger.LogDebug(s"APPhoneSystem: Message added, total messages: \(this.contact.GetMessageCount())");

        if !IsDefined(player) {
            APLogger.LogDebug("APPhoneSystem: Player is null, skipping HUD notification");
            return;
        }
        let phoneSystem: ref<PhoneExtensionSystem> = PhoneExtensionSystem.GetInstance(player);
        if !IsDefined(phoneSystem) {
            APLogger.LogDebug("APPhoneSystem: PhoneExtensionSystem is null, skipping HUD notification");
            return;
        }
        APLogger.LogDebug("APPhoneSystem: Pushing HUD notification");
        phoneSystem.NotifyNewMessageCustom(
            APConstants.GetArchipelagoContactHash(),
            senderName,
            s"Sent you \(itemDisplayName)"
        );
    }
}