module Archipelago

public class APTrapSystem extends ScriptableSystem {
    public let ForceMaxTacSpawn: Bool;
    public let GreyDurationMultiplier: Float;
    public let BlinkDurationMultiplier: Float;

    public func DoTrap(trap: String) -> Void {
        APLogger.LogDebug(s"Got Trap: \(trap)");
        if StrCmp("ap_trp_mostWanted", trap) == 0 {
            APTrapSystem.MostWantedTrap();
            return;
        }
        if StrCmp("ap_trp_randomDebuff", trap) == 0 {
            APTrapSystem.ApplyRandomDebuff();
            return;
        }
        if StrCmp("ap_trp_drunk", trap) == 0 {
            APTrapSystem.ApplyDrunkEffect();
            return;
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

    public static func MostWantedTrap() -> Void {
        APLogger.LogDebug(s"MostWantedTrap: Starting trap execution");
        let preventionSystem = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"PreventionSystem") as PreventionSystem;   
        let APTrapSystem: ref<APTrapSystem> = GameInstance.GetScriptableSystemsContainer(GetGameInstance()).Get(n"Archipelago.APTrapSystem") as APTrapSystem;     
        if !IsDefined(preventionSystem) {
            APLogger.LogDebug(s"MostWantedTrap: PreventionSystem is NULL - trap aborted");
            return;
        }

        APLogger.LogDebug(s"MostWantedTrap: PreventionSystem found, setting wanted level to Heat_5");
        let wantedLevel: ref<SetWantedLevel> = new SetWantedLevel();
        wantedLevel.m_forceGreyStars = false;
        wantedLevel.m_forcePlayerPositionAsLastCrimePoint = true;
        wantedLevel.m_forceIgnoreSecurityAreas = false;
        wantedLevel.m_wantedLevel = EPreventionHeatStage.Heat_5;
        APTrapSystem.GreyDurationMultiplier = 50.0;
        APTrapSystem.BlinkDurationMultiplier = 10.0;
        APLogger.LogDebug(s"MostWantedTrap: GreyDurationMultiplier=\(APTrapSystem.GreyDurationMultiplier), BlinkDurationMultiplier=\(APTrapSystem.BlinkDurationMultiplier)");
        preventionSystem.OnSetWantedLevel(wantedLevel);
        APLogger.LogDebug(s"MostWantedTrap: OnSetWantedLevel called successfully");
    }

    public static func ApplyRandomDebuff() -> Void {
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
        APLogger.LogDebug(s"StartSearchingTimerRequest: AP multiplier active = \(multiplier)");

        if !IsDefined(this.m_preventionDataTable) {
            APLogger.LogDebug(s"StartSearchingTimerRequest: m_preventionDataTable is NULL - falling back to wrappedMethod");
            wrappedMethod();
            return;
        }

        let request: ref<PreventionSearchingStatusRequest> = new PreventionSearchingStatusRequest();
        let baseTime: Float = this.m_preventionDataTable.StateGreyStarTime();
        let duration: Float = baseTime * multiplier;
        APLogger.LogDebug(s"StartSearchingTimerRequest: baseTime=\(baseTime), duration=\(duration)");
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
        let adjustedDuration: Float = duration * multiplier;
        APLogger.LogDebug(s"StartBlinkingTimerRequest: AP multiplier active = \(multiplier), baseDuration=\(duration), adjustedDuration=\(adjustedDuration)");
        wrappedMethod(adjustedDuration, lockWhileBlinking, telemetryInfo);
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
        let multiplier: Float = APTrapSystem.GreyDurationMultiplier;
        APTrapSystem.GreyDurationMultiplier = 0.0;
        let adjusted: Float = duration * multiplier;
        APLogger.LogDebug(s"GetSoftDeescalationGreyStarsDuration: AP multiplier active = \(multiplier), baseDuration=\(duration), adjustedDuration=\(adjusted)");
        return adjusted;
    }
    return duration;
}