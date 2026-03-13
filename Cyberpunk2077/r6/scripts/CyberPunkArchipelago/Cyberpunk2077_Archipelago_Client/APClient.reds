module Archipelago

public class APGameSystem extends ScriptableSystem {
    let items: array<String>;
    let listenerID: Uint32;

    public func OnAttach() -> Void {
        LogChannel(n"DEBUG", "Cyberpunk 2077 Archipelago Plugin Initialized");

    }
    
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

    public func AddQuestKey(questKey: String) -> Void {
        let questSystem: ref<QuestsSystem> = GameInstance.GetQuestsSystem(this.GetGameInstance()) as QuestsSystem;
        if IsDefined(questSystem) {
            questSystem.SetFact(StringToName(questKey), 1);
        }
    }

    public func AddCyberware(cyberware: String) -> Void {
        
    }

    public func AddSkillPoint(skillPoint: String) -> Void {
        
    }

    public func DoTrap(trapName: String) {
        
    }
}

@wrapMethod(PlayerPuppet)
protected cb func OnMakePlayerVisibleAfterSpawn(evt: ref<EndGracePeriodAfterSpawn>) -> Bool {
    let result = wrappedMethod(evt);
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    if IsDefined(APGameState) {
        APGameState.HandlePlayerRespawn();
    }
    return result;
}

@wrapMethod(MenuScenario_Idle)
protected cb func OnShowDeathMenu() -> Bool {
    let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
    let APGameState: ref<APGameState> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.APGameState") as APGameState;
    if IsDefined(APGameState) && APGameState.diedFromDeathLink {
        LogChannel(n"DEBUG", "Player died due to Deathlink");
        return wrappedMethod();
    }
    if IsDefined(tcpService) {
        tcpService.SendDeathLink();
    }
    return wrappedMethod();
}

@wrapMethod(JournalNotificationQueue)
protected cb func OnJournalUpdate(hash: Uint32, className: CName, notifyOption: JournalNotifyOption, changeType: JournalChangeType) -> Bool {
    // 1. Let the vanilla UI logic run first so the player still sees their banner
    let result = wrappedMethod(hash, className, notifyOption, changeType);
    
    // 2. Fetch the Journal Manager
    let player: ref<PlayerPuppet> = this.GetPlayerControlledObject() as PlayerPuppet;
    if !IsDefined(player) { return result; }
    
    let journalMgr: ref<JournalManager> = GameInstance.GetJournalManager(player.GetGame());
    
    // 3. Get the specific journal entry that just triggered the UI update
    let entry: wref<JournalEntry> = journalMgr.GetEntry(hash);
    
    // 4. THE FILTER: Cast it specifically to a JournalQuest. 
    // This is crucial because it filters out minor updates like finding a shard, 
    // getting a text message, or completing a sub-objective (JournalQuestObjective).
    let questEntry: wref<JournalQuest> = entry as JournalQuest;
    
    if IsDefined(questEntry) {
        // 5. Check if the quest's overall state changed to Completed
        let state: gameJournalEntryState = journalMgr.GetEntryState(questEntry);
        
        if Equals(state, gameJournalEntryState.Succeeded) {
            
            // 6. Extract the string ID! (e.g., "q301_crash")
            let questStringId: String = questEntry.GetId();
            LogChannel(n"DEBUG", "UI POPUP INTERCEPTED! Quest Completed: " + questStringId);
            
            // 7. Fire to the Python Server
            let tcpService: ref<TCPClient> = GameInstance.GetScriptableServiceContainer().GetService(n"Archipelago.TCPClient") as TCPClient;
            if IsDefined(tcpService) {
                tcpService.SendCheck(questStringId);
            }
        }
    }
    
    return result;
}