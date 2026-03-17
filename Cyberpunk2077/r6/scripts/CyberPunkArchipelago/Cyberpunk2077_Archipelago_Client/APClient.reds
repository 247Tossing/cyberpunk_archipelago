module Archipelago

public class APGameSystem extends ScriptableSystem {
    let listenerID: Uint32;

    public func OnAttach() -> Void {
        ////LogChannel(n"INFO", "Cyberpunk 2077 System Ready");
    }

    public func SyncData() -> Void {
        let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
        let gameStateItems: ref<APItemList> = APGameState.GetItems();
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        //LogChannel(n"INFO", "Starting Sync");
        ////LogChannel(n"DEBUG", s"Game State Item List has \(ArraySize(gameStateItems.Items)) Items");
        for item in gameStateItems.Items {
            // Try to get the item from the FactsDB.
            let itemCountFromFact: Int32 = questSystem.GetFact(StringToName(item.itemID));
            let stateCount = item.totalFromAP;

            ////LogChannel(n"DEBUG", s"Processing Item: \(item.itemID)");
            ////LogChannel(n"DEBUG", s"Local Item Count Is: \(itemCountFromFact) State Count is: \(stateCount)");

            // If state has more than local, give the difference to player
            if itemCountFromFact < stateCount {
                let difference: Int32 = stateCount - itemCountFromFact;
                ////LogChannel(n"DEBUG", s"Syncing \(difference)x \(item.itemID) to player");

                if StrCmp(item.itemID, "Items.money") == 0
                {
                    // For money, add the difference and update persistent list
                    this.AddEddies(difference);
                    let totalWithDifference: Int32 = itemCountFromFact + difference;
                    questSystem.SetFact(StringToName(item.itemID), totalWithDifference);
                }
                else
                {
                    // For regular items, give each one to player
                    let i: Int32 = 0;
                    while i < difference {
                        this.AddInventoryItem(item.itemID);
                        i += 1;
                    }
                    let totalWithDifference: Int32 = itemCountFromFact + difference;
                    questSystem.SetFact(StringToName(item.itemID), totalWithDifference);
                }
                ////LogChannel(n"DEBUG", s"Sync complete for \(item.itemID)");
            }
        }
        //LogChannel(n"INFO", "Sync Complete");
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
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        if IsDefined(questSystem) {
            ////LogChannel(n"DEBUG", "Adding Quest Key: " + questKey);
            questSystem.SetFact(StringToName(questKey), 1);
        }
    }

    public func AddCyberware(cyberware: String) -> Void {
        //to be implemented
    }

    public func AddSkillPoint(skillPoint: String) -> Void {
        //let pds: ref<PlayerDevelopmentSystem> = PlayerDevelopmentSystem.GetInstance(GameInstance.GetPlayerSystem(this.GetGameInstance()) as GameObject);
         
    }

    public func AddInventoryItem(item: String) -> Void {
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        if !IsDefined(player) {
            return; 
        }

        let totalWithDifference: Int32 = questSystem.GetFact(StringToName(item)) + 1;
        questSystem.SetFact(StringToName(item), totalWithDifference);
        let transactionSystem: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.GetGameInstance());
        let tdbid: TweakDBID = TDBID.Create(item);
        let invItem: ItemID = ItemID.FromTDBID(tdbid);

        transactionSystem.GiveItem(player, invItem, 1);

        ////LogChannel(n"INFO", s"Gave Item \(item)");
    }

    public func AddEddies(amount: Int32) -> Void {
        let player: ref<GameObject> = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;

        if !IsDefined(player) {
            return; 
        }

        let transactionSystem: ref<TransactionSystem> = GameInstance.GetTransactionSystem(this.GetGameInstance());
        let moneyId: ItemID = ItemID.FromTDBID(t"Items.money");
        let totalWithDifference: Int32 = questSystem.GetFact(StringToName("Items.money")) + amount;
        questSystem.SetFact(StringToName("Items.money"), totalWithDifference);
        transactionSystem.GiveItem(player, moneyId, amount);

        ////LogChannel(n"INFO", "Gave Player Eddies");
    }

    public func DoTrap(trapName: String) {
        
    }
}

// Making sure that the player is respawned before allowing another Deathlink call.
@wrapMethod(PlayerPuppet)
protected cb func OnMakePlayerVisibleAfterSpawn(evt: ref<EndGracePeriodAfterSpawn>) -> Bool {
    let result = wrappedMethod(evt);
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    let APGameSystem: ref<APGameSystem> = GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;
    ////LogChannel(n"DEBUG", s"Character Visible");
    if IsDefined(APGameState) {
        ////LogChannel(n"DEBUG", "AP Game State Defined");
        APGameState.HandlePlayerRespawn();
        APGameSystem.SyncData();
    }
    
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
        //LogChannel(n"INFO", "Death caused by Deathlink"); // This makes sure the game doesn't break if it gets multiple deathlink requests back to back before the player respawns.
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
            ////LogChannel(n"DEBUG", "Quest Completed: " + questStringId);
            
            // send to the archipelago server
            let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
            if IsDefined(tcpService) {
                tcpService.SendCheck(questStringId);
            }
        }
    }
    
    return result;
}
