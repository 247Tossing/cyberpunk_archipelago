module Archipelago

public class APTrapSystem extends ScriptableSystem {
    public let ForceMaxTacSpawn: Bool;
    public let GreyDurationMultiplier: Float;
    public let BlinkDurationMultiplier: Float;

    public func DoTrap(trap: String) -> Void {
        return;
        APLogger.LogDebug(s"Got Trap: \(trap)");
        switch trap {
            case "ap_trp_mostWanted":
                this.MostWantedTrap();
            case "ap_trp_randomDebuff":
                this.ApplyRandomDebuff();
            case "ap_trp_drunk":
                APTrapSystem.ApplyDrunkEffect();
        }
    }

    public static func ApplyDrunkEffect() -> Void {
    let player = GameInstance.GetPlayerSystem(GetGameInstance()).GetLocalPlayerMainGameObject();
    
    if IsDefined(player) {
        let drunkEffect = t"BaseStatusEffect.Drunk"; 
        
        // Applying the effect multiple times stacks it, increasing intensity and duration. 
        // 4 applications is the max multiplier.
        StatusEffectHelper.ApplyStatusEffect(player, drunkEffect, player.GetEntityID());
        StatusEffectHelper.ApplyStatusEffect(player, drunkEffect, player.GetEntityID());
        StatusEffectHelper.ApplyStatusEffect(player, drunkEffect, player.GetEntityID());
        StatusEffectHelper.ApplyStatusEffect(player, drunkEffect, player.GetEntityID());
        APLogger.LogDebug(s"Drunk applied");
    }
}

    private func MostWantedTrap() -> Void {
    let preventionSystem = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"PreventionSystem") as PreventionSystem;        
    if IsDefined(preventionSystem) {
            let wantedLevel: ref<SetWantedLevel> = new SetWantedLevel();
            wantedLevel.m_forceGreyStars = false;
            wantedLevel.m_forcePlayerPositionAsLastCrimePoint = true;
            wantedLevel.m_forceIgnoreSecurityAreas = false;
            wantedLevel.m_wantedLevel = EPreventionHeatStage.Heat_5;
            this.GreyDurationMultiplier = 5000.0;
            this.BlinkDurationMultiplier = 10.0;
            preventionSystem.OnSetWantedLevel(wantedLevel);
        }
    }

    private func ApplyRandomDebuff() -> Void {
        let player = GameInstance.GetPlayerSystem(GetGameInstance()).GetLocalPlayerMainGameObject();
        
        if IsDefined(player) {
            let badEffects: array<TweakDBID> = [
                t"BaseStatusEffect.Bleeding",
                t"BaseStatusEffect.Burning",
                t"BaseStatusEffect.Electrocuted",
                t"BaseStatusEffect.Poisoned",
                t"BaseStatusEffect.Blind",       // Reboot Optics
                t"BaseStatusEffect.EMP",         // Disables cyberware temporarily
                t"BaseStatusEffect.Knockdown"    // Physically throws V to the ground
            ];
            
            let randomIndex = RandRange(0, ArraySize(badEffects));
            
            let chosenEffect = badEffects[randomIndex];

            StatusEffectHelper.ApplyStatusEffect(player, chosenEffect, player.GetEntityID());

            APLogger.LogDebug(s"Trap Triggered: V was hit with effect index \(randomIndex)");
        }
    }
}

@wrapMethod(PreventionSystem)
private final func CanRequestAVSpawn() -> Bool {
    let APTrapSystem: ref<APTrapSystem> = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"Archipelago.APTrapSystem") as APTrapSystem;

    if IsDefined(APTrapSystem) && APTrapSystem.ForceMaxTacSpawn {
        APTrapSystem.ForceMaxTacSpawn = false; // Reset the flag so it only applies to one spawn
        return true;
    }
    return wrappedMethod();
}

@wrapMethod(PreventionSystem)
private final func StartSearchingTimerRequest() -> Void {
    let APTrapSystem: ref<APTrapSystem> = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"Archipelago.APTrapSystem") as APTrapSystem;

    if IsDefined(APTrapSystem) && APTrapSystem.GreyDurationMultiplier > 0.0 {
        let multiplier: Float = APTrapSystem.GreyDurationMultiplier;
        APTrapSystem.GreyDurationMultiplier = 0.0;
        let request: ref<PreventionSearchingStatusRequest> = new PreventionSearchingStatusRequest();
        let duration: Float = this.m_preventionDataTable.StateGreyStarTime() * multiplier;
        GameInstance.GetDelaySystem(this.GetGameInstance()).DelayScriptableSystemRequest(n"PreventionSystem", request, duration);
        return;
    }
    wrappedMethod();
}

@wrapMethod(PreventionSystem)
private final func StartBlinkingTimerRequest(duration: Float, lockWhileBlinking: Bool, telemetryInfo: String) -> Void {
    let APTrapSystem: ref<APTrapSystem> = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"Archipelago.APTrapSystem") as APTrapSystem;
    
    if IsDefined(APTrapSystem) && APTrapSystem.BlinkDurationMultiplier > 0.0 {
        let multiplier: Float = APTrapSystem.BlinkDurationMultiplier;
        APTrapSystem.BlinkDurationMultiplier = 0.0;
        wrappedMethod(duration * multiplier, lockWhileBlinking, telemetryInfo);
        return;
    }
    wrappedMethod(duration, lockWhileBlinking, telemetryInfo);
}

// cover the soft deescalation path too
@wrapMethod(PreventionSystem)
private final func GetSoftDeescalationGreyStarsDuration() -> Float {
    let duration: Float = wrappedMethod();
    let APTrapSystem: ref<APTrapSystem> = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"Archipelago.APTrapSystem") as APTrapSystem;
    if IsDefined(APTrapSystem) && APTrapSystem.GreyDurationMultiplier > 0.0 {
        return duration * APTrapSystem.GreyDurationMultiplier;
    }
    return duration;
}