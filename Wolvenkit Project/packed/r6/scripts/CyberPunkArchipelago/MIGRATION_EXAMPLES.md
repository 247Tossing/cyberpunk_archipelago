# Migration Examples - Before & After

This document shows concrete examples of how to refactor existing code using the new foundation classes.

---

## Example 1: Service Registry

### Before:
```redscript
let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
```

### After:
```redscript
let services: ref<APServiceRegistry> = APServiceRegistry.GetInstance();
let gameSystem: ref<APGameSystem> = services.GetGameSystem();
let gameState: ref<APGameState> = services.GetGameState();
let tcpClient: ref<TCPClient> = services.GetTCPClient();
let questSystem: ref<QuestsSystem> = services.GetQuestsSystem();
let player: ref<GameObject> = services.GetPlayer();
```

---

## Example 2: Item Parsing

### Before (APGameState.reds:42-72):
```redscript
public func HandleItemSync(item: String) -> Void {
    let parts: array<String> = StrSplit(item, "_");
    if ArraySize(parts) >= 2 {
        let apSignature = parts[0];
        let itemType = parts[1];
        if StrCmp(apSignature, "ap") != 0 {
            return;
        }
        if StrCmp(itemType, "qk") == 0 {
            this.HandleQuestKeyReceived(item);
        }
        if StrCmp(itemType, "ed") == 0 {
            let amount: Int32 = StringToInt(parts[3]);
            this.items.AddItem("Items.money", amount);
        }
        if StrCmp(itemType, "inv") == 0 {
            let itemId: String = parts[2];
            this.items.AddItem(itemId, 1);
        }
    }
}
```

### After:
```redscript
public func HandleItemSync(item: String) -> Void {
    if !APItemParser.IsValidAPItem(item) {
        return;
    }

    if APItemParser.IsQuestKey(item) {
        this.HandleQuestKeyReceived(item);
    }
    else if APItemParser.IsEddies(item) {
        let amount: Int32 = APItemParser.ParseEddiesAmount(item);
        this.items.AddItem(APConstants.GetMoneyItemId(), amount);
    }
    else if APItemParser.IsInventoryItem(item) {
        let itemId: String = APItemParser.ParseInventoryItemId(item);
        this.items.AddItem(itemId, 1);
    }
}
```

---

## Example 3: Constants

### Before (scattered throughout):
```redscript
questSystem.SetFact(n"ap_dat_watson", 1);
questSystem.SetFact(StringToName("ap_dat_westbrookAccessToken"), 1);
if questSystem.GetFact(n"q000_done") == 0 { ... }

if StrCmp(parts[0], "HELLO") == 0 {
    if StrCmp(status, "OK") == 0 {
        // ...
    }
}
```

### After:
```redscript
questSystem.SetFact(StringToName(APConstants.GetWatsonAccessToken()), 1);
questSystem.SetFact(StringToName(APConstants.GetWestbrookAccessToken()), 1);
if questSystem.GetFact(StringToName(APConstants.GetQuestQ000Done())) == 0 { ... }

if StrCmp(command, APConstants.GetProtocolHello()) == 0 {
    if APItemParser.IsProtocolStatusOk(status) {
        // ...
    }
}
```

---

## Example 4: District Enforcer

### Before (APClient.reds:54-78):
```redscript
public func HandleDistrictRestriction(district: String) -> Void {
    let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    let districtEnforcer: ref<APDistrictEnforcer> = new APDistrictEnforcer(); // CREATES NEW EVERY TIME!

    if questSystem.GetFact(n"q000_done") == 0 || questSystem.GetFact(n"q001_done") == 0 {
        return;
    }

    if this.GetDistrictUnlockStatus(districtEnforcer.ParseEnumToDistrictID(districtEnforcer.GetMajorDistrict(district))) {
        return;
    }

    let player = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
    let currentPos: Vector4 = player.GetWorldPosition();
    // ... teleport code
}
```

### After:
```redscript
public func HandleDistrictRestriction(district: String) -> Void {
    let districtManager: ref<APDistrictManager> = new APDistrictManager();
    districtManager.Initialize();
    districtManager.HandleDistrictRestriction(district);
}
```

---

## Example 5: Inventory Operations

### Before (APClient.reds:148-164):
```redscript
public func AddInventoryItem(item: String) -> Void {
    let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
    let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if !IsDefined(player) {
        return;
    }

    let totalWithDifference: Int32 = questSystem.GetFact(StringToName(item)) + 1;
    questSystem.SetFact(StringToName(item), totalWithDifference);
    let transactionSystem: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.GetGameInstance());
    let tdbid: TweakDBID = TDBID.Create(item);
    let invItem: ItemID = ItemID.FromTDBID(tdbid);

    transactionSystem.GiveItem(player, invItem, 1);
}
```

### After:
```redscript
public func AddInventoryItem(item: String) -> Void {
    let inventoryHandler: ref<APInventoryHandler> = new APInventoryHandler();

    if inventoryHandler.GiveInventoryItem(item, 1) {
        inventoryHandler.IncrementItemFact(item, 1);
    }
}
```

---

## Example 6: Quest Operations

### Before:
```redscript
public func AddQuestKey(questKey: String) -> Void {
    let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance());
    if IsDefined(questSystem) {
        questSystem.SetFact(StringToName(questKey), 1);
    }
}

// Somewhere else:
if questSystem.GetFact(n"q000_done") == 0 || questSystem.GetFact(n"q001_done") == 0 {
    return;
}
```

### After:
```redscript
public func AddQuestKey(questKey: String) -> Void {
    let questHandler: ref<APQuestHandler> = new APQuestHandler();
    questHandler.SetQuestKey(questKey);
}

// Somewhere else:
let questHandler: ref<APQuestHandler> = new APQuestHandler();
if !questHandler.IsLifepathIntroComplete() {
    return;
}
```

---

## Example 7: Protocol Message Parsing

### Before (TCPClient.reds:259-286):
```redscript
private func HandleHelloResponse(response: String) -> Void {
    let parts: array<String> = StrSplit(response, ":");

    if ArraySize(parts) == 3 {
        let command: String = parts[0];
        let serverVersion: String = parts[1];
        let status: String = parts[2];

        if StrCmp(command, "HELLO") == 0 {
            if StrCmp(status, "OK") == 0 {
                this.SendAPConnectRequest();
            } else if StrCmp(status, "FAIL") == 0 {
                APLogger.LogError("Version mismatch!");
            }
        }
    } else {
        APLogger.LogError("Malformed HELLO response");
    }
}
```

### After:
```redscript
private func HandleHelloResponse(response: String) -> Void {
    if !APItemParser.ValidateProtocolParts(response, 3) {
        APLogger.LogError("Malformed HELLO response");
        return;
    }

    let command: String = APItemParser.GetProtocolCommand(response);
    let status: String = APItemParser.GetProtocolStatus(response);

    if StrCmp(command, APConstants.GetProtocolHello()) == 0 {
        if APItemParser.IsProtocolStatusOk(status) {
            this.SendAPConnectRequest();
        } else if APItemParser.IsProtocolStatusFail(status) {
            APLogger.LogError("Version mismatch!");
        }
    }
}
```

---

## Example 8: Item List Parsing

### Before (TCPClient.reds:337-373):
```redscript
private func HandleSyncItemsResponse(response: String) -> Void {
    let parts: array<String> = StrSplit(response, ":");
    if ArraySize(parts) >= 2 {
        let command: String = parts[0];
        let itemsHeader: String = parts[1];
        let itemsString: String = parts[2];

        if StrCmp(command, "SYNC_ITEMS") == 0 {
            if StrCmp(itemsHeader, "ITEMS") == 0 {
                let items: array<String> = StrSplit(itemsString, ",");
                // Process items...
            }
        }
    }
}
```

### After:
```redscript
private func HandleSyncItemsResponse(response: String) -> Void {
    if !APItemParser.ValidateProtocolParts(response, 3) {
        APLogger.LogError("Malformed SYNC_ITEMS response");
        return;
    }

    let parts: array<String> = APItemParser.ParseProtocolMessage(response);
    let command: String = parts[0];
    let itemsHeader: String = parts[1];
    let itemsString: String = parts[2];

    if StrCmp(command, APConstants.GetProtocolSyncItems()) == 0 {
        if StrCmp(itemsHeader, "ITEMS") == 0 {
            let items: array<String> = APItemParser.ParseItemList(itemsString);
            // Process items...
        }
    }
}
```

---

## Pattern: Error Handling

### Before:
```redscript
let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
if !IsDefined(player) {
    return;
}
// Use player...
```

### After:
```redscript
let services: ref<APServiceRegistry> = APServiceRegistry.GetInstance();
let player: ref<GameObject> = services.GetPlayer();

if !IsDefined(player) {
    APLogger.LogWarning("Function: Cannot proceed - player not available");
    return;
}
// Use player...
```

---

## Quick Reference

### Service Access:
```redscript
let services: ref<APServiceRegistry> = APServiceRegistry.GetInstance();
let gameSystem: ref<APGameSystem> = services.GetGameSystem();
let gameState: ref<APGameState> = services.GetGameState();
let player: ref<GameObject> = services.GetPlayer();
```

### Item Parsing:
```redscript
if APItemParser.IsEddies(item) {
    let amount: Int32 = APItemParser.ParseEddiesAmount(item);
}
if APItemParser.IsInventoryItem(item) {
    let itemId: String = APItemParser.ParseInventoryItemId(item);
}
```

### Constants:
```redscript
APConstants.GetWatsonAccessToken()
APConstants.GetProtocolHello()
APConstants.GetMoneyItemId()
```

### Handlers:
```redscript
let inventoryHandler: ref<APInventoryHandler> = new APInventoryHandler();
inventoryHandler.GiveInventoryItem(itemId, 1);

let questHandler: ref<APQuestHandler> = new APQuestHandler();
questHandler.SetQuestKey(keyId);

let districtManager: ref<APDistrictManager> = new APDistrictManager();
districtManager.UnlockDistrict(districtId);
```

### Singleton:
```redscript
let enforcer: ref<APDistrictEnforcer> = APDistrictEnforcer.GetInstance();
let safePoint: Vector4 = enforcer.GetNearestSafePoint(currentPos);
```
