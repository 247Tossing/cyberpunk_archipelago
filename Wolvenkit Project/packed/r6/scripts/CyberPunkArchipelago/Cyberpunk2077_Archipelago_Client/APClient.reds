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
        APLogger.LogInfo("Starting Check Sync With AP Server");
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if !IsDefined(tcpClient){
            APLogger.LogError("Failed to get TCP client");
            return;
        }
        tcpClient.SendSyncCheckRequest();
    }

    public func HandleSyncCheck(locations: array<String>) -> Void {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
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
        let gameStateItems: ref<APItemList> = APGameState.GetItems();
        APLogger.LogInfo("Starting Item Sync");

        for item in gameStateItems.Items { 
            // Try to get the item from the FactsDB
            let itemCountFromFact: Int32 = this.inventoryHandler.GetItemFactCount(item.itemID);
            let stateCount: Int32 = item.totalFromAP;

            // If state has more than local, give the difference to player
            if itemCountFromFact < stateCount {
                let difference: Int32 = stateCount - itemCountFromFact;

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
                    this.HandleDistrictUnlock(item.itemID);
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
        if IsDefined(this.districtManager) {
            this.districtManager.HandleDistrictRestriction(district);
        } else {
            APLogger.LogWarning("APGameSystem: District manager not available");
        }
    }

    public func HandleDistrictUnlock(district: String) -> Void {
        if IsDefined(this.districtManager) {
            this.districtManager.UnlockDistrict(district);
        } else {
            APLogger.LogWarning("APGameSystem: District manager not available");
        }
    }

    public func GetDistrictUnlockStatus(district: String) -> Bool {
        if IsDefined(this.districtManager) {
            return this.districtManager.IsDistrictUnlocked(district);
        }
        return false;
    }

    public func HandleTarotCollected(value: Int32) -> Void {
        this.SendTarotFound(value);
    }

    //Progressive Items
    public func HandleProgressiveItem(item: String) -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        if questSystem.GetFact(StringToName(item)) < 1 {
            this.AddInventoryItem(APItemProgression.GetProgressiveItem(item, 1));
            APGameState.items.AddItem(APItemProgression.GetProgressiveItem(item, 1), 1);
        }
        else
        {
            let progressionLevel: Int32 = questSystem.GetFact(StringToName(item)) + 1;
            this.AddInventoryItem(APItemProgression.GetProgressiveItem(item, progressionLevel));
            APGameState.items.AddItem(APItemProgression.GetProgressiveItem(item, 1), 1);
        }
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
            APLogger.LogWarning("APGameSystem: Quest handler not available");
        }
    }

    public func AddCyberware(cyberware: String) -> Void {
        //to be implemented
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
            APLogger.LogWarning("APGameSystem: Inventory handler not available");
        }
    }

    // Delegate to inventory handler
    public func AddEddies(amount: Int32) -> Void {
        if IsDefined(this.inventoryHandler) {
            this.inventoryHandler.GiveEddies(amount);
            this.inventoryHandler.IncrementItemFact(APConstants.GetMoneyItemId(), amount);
        } else {
            APLogger.LogWarning("APGameSystem: Inventory handler not available");
        }
    }

    public func HasItem(itemID: String) -> Bool {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        if questSystem.GetFact(n"itemID") >= 1 {
            return true;
        }
        return false;
    }

    public func DoTrap(trapName: String) {
        // To be implemented
    }

    // ===== METHODS MOVED FROM APGameState =====
    // These were business logic that should be in APGameSystem, not the data class

    public func FeedItemsList(itemList: array<String>) -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;

        if !IsDefined(APGameState) || !IsDefined(APGameState.items) {
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

    private func HandleItemSync(item: String, gameState: ref<APGameState>) -> Void {
        if !APItemParser.IsValidAPItem(item) {
            return;
        }

        // Increment NetworkItem counter for each item processed (matches Python's len(received_items))
        gameState.totalNetworkItemsReceived += 1;

        // Always add to persistent storage first so items can be re-synced on save load
        if APItemParser.IsQuestKey(item) {
            // Quest keys are tracked even though they're binary (0 or 1)
            gameState.items.AddItem(item, 1);
            this.AddQuestKey(item);
        }
        else if APItemParser.IsEddies(item) {
            let amount: Int32 = APItemParser.ParseEddiesAmount(item);
            gameState.items.AddItem(APConstants.GetMoneyItemId(), amount);
        }
        else if APItemParser.IsInventoryItem(item) {
            let itemId: String = APItemParser.ParseInventoryItemId(item);
            gameState.items.AddItem(itemId, 1);
        }
        else if APItemParser.IsProgressiveItem(item) {
            // Track progressive items so they can be re-synced on save load
            gameState.items.AddItem(item, 1);
        }
        else if APItemParser.IsDistrictToken(item) {
            // Track district tokens so they can be re-synced on save load
            gameState.items.AddItem(item, 1);
        }
        // Note: Skill points and traps not added as they're not fully implemented
    }

    public func HandleItemReceived(item: String) -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;

        if !APItemParser.IsValidAPItem(item) {
            return;
        }

        // Increment NetworkItem counter for real-time items from queue worker
        if IsDefined(APGameState) {
            APGameState.totalNetworkItemsReceived += 1;
        }

        if APItemParser.IsQuestKey(item) {
            if IsDefined(APGameState.items) {
                APGameState.items.AddItem(item, 1);
            }
            this.AddQuestKey(item);
        }
        else if APItemParser.IsSkillPoint(item) {
            // Not implemented
        }
        else if APItemParser.IsTrap(item) {
            this.DoTrap(item);
        }
        else if APItemParser.IsEddies(item) {
            let amount: Int32 = APItemParser.ParseEddiesAmount(item);
            if IsDefined(APGameState.items) {
                APGameState.items.AddItem(APConstants.GetMoneyItemId(), amount);
            }
            this.AddEddies(amount);
        }
        else if APItemParser.IsInventoryItem(item) {
            let itemId: String = APItemParser.ParseInventoryItemId(item);
            if IsDefined(APGameState.items) {
                APGameState.items.AddItem(itemId, 1);
            }
            this.AddInventoryItem(itemId);
        }
        else if APItemParser.IsProgressiveItem(item) {
            if IsDefined(APGameState.items) {
                APGameState.items.AddItem(item, 1);
            }
            this.HandleProgressiveItem(item);
        }
        else if APItemParser.IsDistrictToken(item) {
            if IsDefined(APGameState.items) {
                APGameState.items.AddItem(item, 1);
            }
            this.HandleDistrictUnlock(item);
        }
    }

    public func SendTarotFound(tarotNumber: Int32) -> Void {
        let tcpClient: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
        if IsDefined(tcpClient) {
            tcpClient.SendCheck(s"\(APConstants.GetTarotCheckPrefix())\(tarotNumber)");
        }
    }
}

@wrapMethod(DistrictManager)
public final func Update(evt: ref<DistrictEnteredEvent>) -> Void {
    let districtString: String = TDBID.ToStringDEBUG(evt.district);
    let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
    APGameSystem.HandleDistrictRestriction(districtString);
    //APLogger.LogInfo(districtString);
}

// Making sure that the player is respawned before allowing another Deathlink call.
@wrapMethod(PlayerPuppet)
protected cb func OnMakePlayerVisibleAfterSpawn(evt: ref<EndGracePeriodAfterSpawn>) -> Bool {
    let result = wrappedMethod(evt);
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
    //APLogger.LogInfo( s"Character Visible");
    if IsDefined(APGameState) {
        //APLogger.LogInfo( "AP Game State Defined");
        APGameState.HandlePlayerRespawn();
        APGameSystem.SyncData();
        APGameSystem.SendSyncChecks();

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
        // 5. Check if the quest's overall state changed to Completed
        let state: gameJournalEntryState = journalMgr.GetEntryState(questEntry);
        
        if Equals(state, gameJournalEntryState.Succeeded) {
            
            // Extract the string ID
            let questStringId: String = questEntry.GetId();
            //APLogger.LogInfo( "Quest Completed: " + questStringId);
            let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(GetGameInstance()) as QuestsSystem;

            // send to the archipelago server
            let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
            if IsDefined(tcpService) {
                questSystem.SetFact(StringToName(s"ap_\(questStringId)"), 1);
                tcpService.SendCheck(questStringId);
            }
        }
    }
    
    return result;
}