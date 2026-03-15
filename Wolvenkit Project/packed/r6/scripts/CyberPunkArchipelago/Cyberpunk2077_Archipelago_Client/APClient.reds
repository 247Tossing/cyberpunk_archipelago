module Archipelago

public class APGameSystem extends ScriptableSystem {
    let items: array<String>;
    let listenerID: Uint32;

    public func OnAttach() -> Void {
        LogChannel(n"DEBUG", "Cyberpunk 2077 Archipelago Plugin Initialized");
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
            LogChannel(n"DEBUG", "Adding Quest Key: " + questKey);
            questSystem.SetFact(StringToName(questKey), 1);
        }
    }

    public func AddCyberware(cyberware: String) -> Void {
        
    }

    public func AddSkillPoint(skillPoint: String) -> Void {
        //let pds: ref<PlayerDevelopmentSystem> = PlayerDevelopmentSystem.GetInstance(GameInstance.GetPlayerSystem(this.GetGameInstance()) as GameObject);
         
    }

    public func DoTrap(trapName: String) {
        
    }

    
}

// Making sure that the player is respawned before allowing another Deathlink call.
@wrapMethod(PlayerPuppet)
protected cb func OnMakePlayerVisibleAfterSpawn(evt: ref<EndGracePeriodAfterSpawn>) -> Bool {
    let result = wrappedMethod(evt);
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    if IsDefined(APGameState) {
        APGameState.HandlePlayerRespawn();
        APGameState.ResyncData();
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
        LogChannel(n"DEBUG", "Player died due to Deathlink");
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
    
    // Fetch the Journal Manager
    let player: ref<PlayerPuppet> = this.GetPlayerControlledObject() as PlayerPuppet;
    if !IsDefined(player) { return result; }
    
    let journalMgr: ref<JournalManager> = GameInstance.GetJournalManager(player.GetGame());
    
    // Get the specific journal entry that just triggered the UI update
    let entry: wref<JournalEntry> = journalMgr.GetEntry(hash);
    
    // Cast it specifically to a JournalQuest. 
    // This is crucial because it filters out minor updates like finding a shard, 
    // getting a text message, or completing a sub-objective (JournalQuestObjective).
    let questEntry: wref<JournalQuest> = entry as JournalQuest;
    
    if IsDefined(questEntry) {
        // 5. Check if the quest's overall state changed to Completed
        let state: gameJournalEntryState = journalMgr.GetEntryState(questEntry);
        
        if Equals(state, gameJournalEntryState.Succeeded) {
            
            // Extract the string ID
            let questStringId: String = questEntry.GetId();
            //LogChannel(n"DEBUG", "UI POPUP INTERCEPTED! Quest Completed: " + questStringId);
            
            // send to the archipelago server
            let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
            if IsDefined(tcpService) {
                tcpService.SendCheck(questStringId);
            }
        }
    }
    
    return result;
}