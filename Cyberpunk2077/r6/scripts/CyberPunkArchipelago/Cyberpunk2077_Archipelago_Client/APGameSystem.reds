module Archipelago

public class APGameSystem extends ScriptableSystem {
    let listenerID: Uint32; 

    // Cached handler references (initialized in OnAttach)
    private let inventoryHandler: ref<APInventoryHandler>;
    private let questHandler: ref<APQuestHandler>;
    private let districtManager: ref<APDistrictManager>;

    public func OnAttach() -> Void {
        // Cache handler references to avoid repeated container lookups
        let container: ref<ScriptableSystemsContainer> = this.GetGameInstance().GetScriptableSystemsContainer();
        this.inventoryHandler = container.Get(n"Archipelago.APInventoryHandler") as APInventoryHandler;
        this.questHandler = container.Get(n"Archipelago.APQuestHandler") as APQuestHandler;
        this.districtManager = container.Get(n"Archipelago.APDistrictManager") as APDistrictManager;
        APLogger.LogInfo("Cyberpunk 2077 Archipelago System Ready");
    }

    public func SendSyncChecks() -> Void {
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if !IsDefined(tcpClient){
            APLogger.LogError("Failed to get TCP client");
            return;
        }
        if !tcpClient.IsConnected() {
            return;
        }
        APLogger.LogInfo("Starting Check Sync With AP Server");
        let locations: array<String> = APArchipelagoIdMappings.GetAllLocationIds();
        this.HandleSyncCheck(locations);
    }

    public func HandleSyncCheck(locations: array<String>) -> Void {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if !IsDefined(questSystem) {
            APLogger.LogError("HandleSyncCheck: QuestsSystem is null - game world may not be fully loaded yet.");
            return;
        }
        if !IsDefined(tcpClient) {
            APLogger.LogError("HandleSyncCheck: TCPClient is null.");
            return;
        }
        APLogger.LogInfo("Starting Check Sync");
        for loc in locations {
            //APLogger.LogInfo(s"Checking: \(loc)");
            if questSystem.GetFact(StringToName(s"ap_\(loc)")) >= 1 {
               tcpClient.SendCheck(loc);
            }
        }
        APLogger.LogInfo("Check Sync Complete");
    }

    public func SyncData() -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if !IsDefined(APGameState) {
            APLogger.LogDebug("APGameSystem: Cannot sync data - game state not available");
            return;
        }

        let gameStateItems: ref<APItemList> = APGameState.GetItems();
        if !IsDefined(gameStateItems) {
            APLogger.LogDebug("APGameSystem: Cannot sync data - item list not available");
            return;
        }

        // Handlers are cached in OnAttach; ScriptableSystems (and this cache) are recreated on every
        // save load, so guard against SyncData running before OnAttach has resolved them.
        if !IsDefined(this.inventoryHandler) || !IsDefined(this.questHandler) {
            APLogger.LogDebug("APGameSystem: Cannot sync data - inventory/quest handler not available");
            return;
        }

        APLogger.LogInfo(s"Starting Item Sync - \(ArraySize(gameStateItems.Items)) tracked item(s), restrictByMajorDistrict=\(APGameState.restrictByMajorDistrict)");

        for item in gameStateItems.Items { 
            // Try to get the item from the FactsDB
            let itemCountFromFact: Int32 = this.inventoryHandler.GetItemFactCount(item.itemID);
            let stateCount: Int32 = item.totalFromAP;

            if APItemParser.IsDistrictToken(item.itemID) {
                APLogger.LogDebug(s"SyncData: district token '\(item.itemID)' - factCount=\(itemCountFromFact), totalFromAP=\(stateCount)");
            }

            // If state has more than local, give the difference to player
            if itemCountFromFact < stateCount {
                let difference: Int32 = stateCount - itemCountFromFact;
                APLogger.LogDebug(s"SyncData: '\(item.itemID)' factCount(\(itemCountFromFact)) < totalFromAP(\(stateCount)) - applying difference=\(difference)");

                // Route to appropriate handler based on item type
                if StrCmp(item.itemID, APConstants.GetMoneyItemId()) == 0 {
                    // Money/Eddies
                    this.inventoryHandler.GiveEddies(difference);
                    this.inventoryHandler.IncrementItemFact(item.itemID, difference);
                }
                else if APItemParser.IsQuestKey(item.itemID) {
                    // Quest keys (binary - just set to 1)
                    this.AddQuestKey(item.itemID);
                }
                else if APItemParser.IsProgressiveItem(item.itemID) {
                    // Progressive items (need special handling)
                    let i: Int32 = 0;
                    while i < difference {
                        this.HandleProgressiveItem(item.itemID);
                        i += 1;
                    }
                }
                else if APItemParser.IsDistrictToken(item.itemID) {
                    // District unlock tokens (binary - just unlock)
                    APLogger.LogDebug(s"SyncData: retrying HandleDistrictUnlock('\(item.itemID)')");
                    this.HandleDistrictUnlock(item.itemID);
                }
                else if APItemParser.IsWeaponAuthorization(item.itemID) {
                    // Weapon passes are quest-key style unlocks
                    this.HandleWeaponUnlock(item.itemID);
                }
                else {
                    // Regular inventory items
                    this.inventoryHandler.GiveInventoryItem(item.itemID, difference);
                    this.inventoryHandler.IncrementItemFact(item.itemID, difference);
                }
            }
        }

        // Always ensure Watson is unlocked as starting district
        this.questHandler.SetQuestKey(APConstants.GetWatsonAccessToken());
        APLogger.LogInfo("Item Sync Complete");
    }

    public func HandleDistrictRestriction(district: String) -> Void {
        APLogger.LogDebug(s"APGameSystem: HandleDistrictRestriction('\(district)') - districtManager defined=\(IsDefined(this.districtManager))");
        if IsDefined(this.districtManager) {
            this.districtManager.HandleDistrictRestriction(district);
        } else {
            APLogger.LogDebug("APGameSystem: District manager not available");
        }
    }

    public func HandleDistrictUnlock(district: String) -> Void {
        APLogger.LogDebug(s"APGameSystem: HandleDistrictUnlock('\(district)') - districtManager defined=\(IsDefined(this.districtManager))");
        if IsDefined(this.districtManager) {
            this.districtManager.UnlockDistrict(district);
        } else {
            APLogger.LogDebug("APGameSystem: District manager not available");
        }
    }

    public func HandleWeaponUnlock(weaponAuth: String) -> Void {
        // Weapon unlocks are handled via quest keys for pass-gated restrictions, so just add the quest key
        this.AddQuestKey(weaponAuth);
    }

    public func GetDistrictUnlockStatus(district: String) -> Bool {
        if IsDefined(this.districtManager) {
            let unlocked: Bool = this.districtManager.IsDistrictUnlocked(district);
            APLogger.LogDebug(s"APGameSystem: GetDistrictUnlockStatus('\(district)')=\(unlocked)");
            return unlocked;
        }
        APLogger.LogDebug(s"APGameSystem: GetDistrictUnlockStatus('\(district)') - districtManager not available, returning false");
        return false;
    }

    public func HandleTarotCollected(value: Int32) -> Void {
        this.SendTarotFound(value);
    }

    //Progressive Items
    public func HandleProgressiveItem(item: String) -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if !IsDefined(this.inventoryHandler) {
            APLogger.LogDebug("APGameSystem: Cannot handle progressive item - inventory handler not available");
            return;
        }
        let progressionLevel: Int32 = this.inventoryHandler.GetItemFactCount(item) + 1;
        let resolvedItem: String = APItemProgression.GetProgressiveItem(item, progressionLevel);
        this.AddInventoryItem(resolvedItem);
        if IsDefined(APGameState) {
            APGameState.GetItems().AddItem(resolvedItem, 1);
        }
        this.inventoryHandler.IncrementItemFact(item, 1);
    }

    //Deathlink    
    public func HandleDeathLink() -> Void {
        let player: ref<PlayerPuppet> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject() as PlayerPuppet;
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if IsDefined(player) {
            if IsDefined(APGameState) {
                if !APGameState.diedFromDeathLink {
                    APGameState.DiedFromDeathLink();
                    StatusEffectHelper.ApplyStatusEffect(player, t"BaseStatusEffect.ForceKill");
                }
            }
        }
    }

    // For when the player receives a quest item from the Archipelago server.
    public func AddQuestKey(questKey: String) -> Void {
        if IsDefined(this.questHandler) {
            this.questHandler.SetQuestKey(questKey);
        } else {
            APLogger.LogDebug("APGameSystem: Quest handler not available");
        }
    }
    
    public func AddSkillPoint(skillPoint: String) -> Void {
        //let pds: ref<PlayerDevelopmentSystem> = PlayerDevelopmentSystem.GetInstance(GameInstance.GetPlayerSystem(this.GetGameInstance()) as GameObject);
         
    }

    // Delegate to inventory handler
    public func AddInventoryItem(item: String) -> Void {
        if IsDefined(this.inventoryHandler) {
            this.inventoryHandler.GiveInventoryItem(item, 1);
            this.inventoryHandler.IncrementItemFact(item, 1);
        } else {
            APLogger.LogDebug("APGameSystem: Inventory handler not available");
        }
    }

    // Delegate to inventory handler
    public func AddEddies(amount: Int32) -> Void {
        if IsDefined(this.inventoryHandler) {
            this.inventoryHandler.GiveEddies(amount);
            this.inventoryHandler.IncrementItemFact(APConstants.GetMoneyItemId(), amount);
        } else {
            APLogger.LogDebug("APGameSystem: Inventory handler not available");
        }
    }

    public func HasItem(itemID: String) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        if questSystem.GetFact(StringToName(itemID)) >= 1 {
            return true;
        }
        return false;
    }

    public func FeedItemsList(itemList: array<String>) -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;

        if IsDefined(APGameState) {
            APGameState.items = new APItemList();
        }

        for item in itemList {
            if StrLen(item) > 0 {
                this.HandleItemSync(item, APGameState);
            }
        }

        APLogger.LogInfo(s"Synced \(ArraySize(itemList)) Items from AP Server");

        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if IsDefined(tcpClient) {
            // Send total NetworkItems count (not unique item types) to match Python's len(received_items)
            tcpClient.SendSyncCompleteResponse(APGameState.totalNetworkItemsReceived);
        }
    }

    // Re-applies an already-seen network item (i.e. one the server is resending on reconnect that
    // was already applied during a prior connection). This must never re-trigger one-shot effects
    // like traps, but progression state (quest keys, district tokens, weapon passes) is safe - and
    // necessary - to reconcile here, since it recovers grants that never made it into a quest fact
    // the first time (e.g. the item arrived before the world/quest system was ready).
    public func HandleItemSync(item: String, gameState: ref<APGameState>) -> Void {
        APLogger.LogDebug(s"HandleItemSync: item='\(item)' gameStateDefined=\(IsDefined(gameState))");
        if !IsDefined(gameState) {
            APLogger.LogDebug("HandleItemSync: aborting - gameState not defined");
            return;
        }

        if !APItemParser.IsValidAPItem(item) {
            APLogger.LogDebug(s"HandleItemSync: aborting - '\(item)' is not a valid AP item");
            return;
        }

        // GetItems() lazily creates the list if needed, so this is never null.
        let items: ref<APItemList> = gameState.GetItems();

        // Increment NetworkItem counter for each item processed (matches Python's len(received_items))
        gameState.totalNetworkItemsReceived += 1;

        // Always add to persistent storage first so items can be re-synced on save load
        if APItemParser.IsQuestKey(item) {
            // Quest keys are tracked even though they're binary (0 or 1)
            items.AddItem(item, 1);
            this.AddQuestKey(item);
        }
        else if APItemParser.IsTrap(item) {
            // Traps are one-shot effects - re-syncing a previously-applied item must not re-trigger them.
            APLogger.LogDebug(s"APGameSystem: Skipping trap replay during sync: \(item)");
        }
        else if APItemParser.IsEddies(item) {
            let amount: Int32 = APItemParser.ParseEddiesAmount(item);
            items.AddItem(APConstants.GetMoneyItemId(), amount);
        }
        else if APItemParser.IsInventoryItem(item) {
            let itemId: String = APItemParser.ParseInventoryItemId(item);
            items.AddItem(itemId, 1);
        }
        else if APItemParser.IsProgressiveItem(item) {
            // Track progressive items so they can be re-synced on save load
            items.AddItem(item, 1);
        }
        else if APItemParser.IsDistrictToken(item) {
            // Track district tokens so they can be re-synced on save load, and retry the unlock in
            // case the quest fact never got written the first time this item was received.
            APLogger.LogDebug(s"HandleItemSync: district token '\(item)' - AddItem + retry HandleDistrictUnlock");
            items.AddItem(item, 1);
            this.HandleDistrictUnlock(item);
        }
        else if APItemParser.IsWeaponAuthorization(item) {
            items.AddItem(item, 1);
            this.HandleWeaponUnlock(item);
        }
        // Note: Skill points not added as they're not fully implemented
    }

    public func HandleItemReceived(item: String) -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        APLogger.LogDebug(s"HandleItemReceived: item='\(item)' gameStateDefined=\(IsDefined(APGameState))");

        if !APItemParser.IsValidAPItem(item) {
            APLogger.LogDebug(s"HandleItemReceived: aborting - '\(item)' is not a valid AP item");
            return;
        }

        // GetItems() lazily creates the list if needed, so items is never null once gameState is defined.
        let items: ref<APItemList>;
        if IsDefined(APGameState) {
            items = APGameState.GetItems();
            // Increment NetworkItem counter for real-time items from queue worker
            APGameState.totalNetworkItemsReceived += 1;
        }

        if APItemParser.IsQuestKey(item) {
            if IsDefined(items) {
                items.AddItem(item, 1);
            }
            this.AddQuestKey(item);
        }
        else if APItemParser.IsSkillPoint(item) {
            // Not implemented
        }
        else if APItemParser.IsTrap(item) {
            APLogger.LogDebug(s"APGameSystem: HandleItemReceived called - trap: \(item)");
            let APTrapSystem: ref<APTrapSystem> = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"Archipelago.APTrapSystem") as APTrapSystem;
            if IsDefined(APTrapSystem) {
                APTrapSystem.DoTrap(item);
            }
        }
        else if APItemParser.IsEddies(item) {
            let amount: Int32 = APItemParser.ParseEddiesAmount(item);
            if IsDefined(items) {
                items.AddItem(APConstants.GetMoneyItemId(), amount);
            }
            this.AddEddies(amount);
        }
        else if APItemParser.IsInventoryItem(item) {
            let itemId: String = APItemParser.ParseInventoryItemId(item);
            if IsDefined(items) {
                items.AddItem(itemId, 1);
            }
            this.AddInventoryItem(itemId);
        }
        else if APItemParser.IsProgressiveItem(item) {
            if IsDefined(items) {
                items.AddItem(item, 1);
            }
            this.HandleProgressiveItem(item);
        }
        else if APItemParser.IsDistrictToken(item) {
            APLogger.LogDebug(s"HandleItemReceived: district token '\(item)' - AddItem + HandleDistrictUnlock (live grant)");
            if IsDefined(items) {
                items.AddItem(item, 1);
            }
            this.HandleDistrictUnlock(item);
        }
        else if APItemParser.IsWeaponAuthorization(item) {
            if IsDefined(items) {
                items.AddItem(item, 1);
            }
            this.HandleWeaponUnlock(item);
        }
    }

    public func SendTarotFound(tarotNumber: Int32) -> Void {
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if IsDefined(tcpClient) {
            tcpClient.SendCheck(s"\(APConstants.GetTarotCheckPrefix())\(tarotNumber)");
        }
    }

    public func HandleItemReceivedNotification(senderName: String, itemDisplayName: String) -> Void {
        APLogger.LogDebug(s"APGameSystem: HandleItemReceivedNotification called - sender: \(senderName), item: \(itemDisplayName)");
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        if !IsDefined(APGameState) {
            APLogger.LogError("APGameSystem: APGameState is null");
            return;
        }
        let phoneSystem: ref<APPhoneSystem> = APGameState.GetPhoneSystem();
        if !IsDefined(phoneSystem) {
            APLogger.LogError("APGameSystem: GetPhoneSystem() returned null");
            return;
        }
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
        APLogger.LogDebug(s"APGameSystem: Player defined: \(IsDefined(player))");
        phoneSystem.SendItemNotification(player, senderName, itemDisplayName);
    }
}

@wrapMethod(DistrictManager)
public final func Update(evt: ref<DistrictEnteredEvent>) -> Void {
    let districtString: String = TDBID.ToStringDEBUG(evt.district);
    let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
    APLogger.LogDebug(s"DistrictEnteredEvent fired: rawDistrict='\(districtString)' APGameSystemDefined=\(IsDefined(APGameSystem))");
    if IsDefined(APGameSystem) {
        APGameSystem.HandleDistrictRestriction(districtString);
    }
}

// Making sure that the player is respawned before allowing another Deathlink call.
@wrapMethod(PlayerPuppet)
protected cb func OnMakePlayerVisibleAfterSpawn(evt: ref<EndGracePeriodAfterSpawn>) -> Bool {
    let result = wrappedMethod(evt);
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
    APLogger.LogDebug(s"OnMakePlayerVisibleAfterSpawn: EndGracePeriodAfterSpawn fired - APGameStateDefined=\(IsDefined(APGameState)), APGameSystemDefined=\(IsDefined(APGameSystem))");
    if IsDefined(APGameState) {
        APLogger.LogDebug("OnSpawn: Running SyncData + SendSyncChecks");
        APGameState.HandlePlayerRespawn();

        // Defer district enforcement until the post-spawn item backlog (if connected) has been
        // fully drained by TCPClient.Pump - see APGameState.itemResyncPending. Must happen before
        // SyncData/SendSyncChecks so any DistrictEnteredEvent firing immediately after spawn is
        // already covered.
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if IsDefined(tcpClient) {
            tcpClient.OnPlayerSpawned();
        }

        APGameSystem.SyncData();
        APGameSystem.SendSyncChecks();

        // Register the Archipelago phone contact on every spawn
        APLogger.LogDebug("OnSpawn: Attempting to register phone contact");
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(GetGameInstance()).GetLocalPlayerMainGameObject();
        let phoneSystem: ref<APPhoneSystem> = APGameState.GetPhoneSystem();
        APLogger.LogDebug(s"OnSpawn: Player defined: \(IsDefined(player)), phoneSystem defined: \(IsDefined(phoneSystem))");
        if IsDefined(player) && IsDefined(phoneSystem) {
            phoneSystem.RegisterContact(player);
        }
    }

    let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(GetGameInstance()) as QuestsSystem;
    questSystem.RegisterListener(n"mq033_grafitti_counter", APGameSystem, n"HandleTarotCollected");
    
    return result;
}

// For sending DeathLinks
@wrapMethod(MenuScenario_Idle)
protected cb func OnShowDeathMenu() -> Bool {
    //if deathlink is disabled, just return
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    if IsDefined(APGameState) && !APGameState.enableDeathLink {
        return wrappedMethod();
    }

    let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
    if IsDefined(APGameState) && APGameState.diedFromDeathLink {
        APLogger.LogInfo( "Death caused by Deathlink"); // This makes sure the game doesn't break if it gets multiple deathlink requests back to back before the player respawns.
        return wrappedMethod();
    }

    if IsDefined(tcpService) {
        //APLogger.LogInfo( "Sending DeathLink");
        tcpService.SendDeathLink();
    }

    return wrappedMethod();
}

//For sending quest completion updates to the Archipelago server.
@wrapMethod(JournalNotificationQueue)
protected cb func OnJournalUpdate(hash: Uint32, className: CName, notifyOption: JournalNotifyOption, changeType: JournalChangeType) -> Bool {
    let result = wrappedMethod(hash, className, notifyOption, changeType);

    let player: ref<PlayerPuppet> = this.GetPlayerControlledObject() as PlayerPuppet;
    if !IsDefined(player) { return result; }
    
    let journalMgr: ref<JournalManager> = GameInstance.GetJournalManager(player.GetGame());
    let entry: wref<JournalEntry> = journalMgr.GetEntry(hash); // Get the specific journal entry that just triggered the UI update
    let questEntry: wref<JournalQuest> = entry as JournalQuest; //Cast it to a quest to get access to what we actually want
    
    if IsDefined(questEntry) {
        let state: gameJournalEntryState = journalMgr.GetEntryState(questEntry);
        let questStringId: String = questEntry.GetId();
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(GetGameInstance()) as QuestsSystem;
        let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;

        if !IsDefined(tcpService) {
            return result;
        }

        // Phantom Liberty path split: Songbird path — Killing Moon started -> Split Quest 1.
        if StrCmp(questStringId, "q306_devils_bargain") == 0 && Equals(state, gameJournalEntryState.Active) {
            APQuestLocationLookup.SendLocationCheck(questSystem, tcpService, "pl_split_quest_1");
            return result;
        }

        // Phantom Liberty path split: Songbird path — Killing Moon completed -> Split Quest 2 + 3.
        if StrCmp(questStringId, "q306_devils_bargain") == 0 && Equals(state, gameJournalEntryState.Succeeded) {
            APQuestLocationLookup.SendLocationCheck(questSystem, tcpService, "pl_split_quest_2");
            APQuestLocationLookup.SendLocationCheck(questSystem, tcpService, "pl_split_quest_3");
            return result;
        }

        if Equals(state, gameJournalEntryState.Succeeded) {
            // Resolve to a stable location ID using explicit quest lookup aliases.
            let locationId: String = APQuestLocationLookup.ResolveLocationId(questStringId);
            //APLogger.LogInfo( "Quest Completed: " + questStringId);

            // Send to the Archipelago server when this quest maps to a tracked location.
            if StrLen(locationId) > 0 {
                APQuestLocationLookup.SendLocationCheck(questSystem, tcpService, locationId);
            }
        }
    }
    
    return result;
}


