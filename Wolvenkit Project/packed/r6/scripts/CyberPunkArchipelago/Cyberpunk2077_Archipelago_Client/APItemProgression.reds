module Archipelago

public class APItemProgression extends ScriptableSystem {

    // Input is the item from the AP server
    // Returns the ID for the progressive item
    public static func GetProgressiveItem(item: String, savedProgressionLevel: Int32) -> String {
        
        switch item {
            case "ap_prog_overheat": return APItemProgression.GetProgressiveOverheat(savedProgressionLevel);
            case "ap_prog_shortCircuit": return APItemProgression.GetProgressiveShortCircuit(savedProgressionLevel);
            case "ap_prog_rebootOptics": return APItemProgression.GetProgressiveRebootOptics(savedProgressionLevel);
            case "ap_prog_contagion": return APItemProgression.GetProgressiveContagion(savedProgressionLevel);
            case "ap_prog_synapseBurnout": return APItemProgression.GetProgressiveSynapseBurnout(savedProgressionLevel);
            case "ap_prog_cyberwareMalfunction": return APItemProgression.GetProgressiveCyberwareMalfunction(savedProgressionLevel);
            case "ap_prog_crippleMovement": return APItemProgression.GetProgressiveCrippleMovement(savedProgressionLevel);
            case "ap_prog_weaponGlitch": return APItemProgression.GetProgressiveWeaponGlitch(savedProgressionLevel);
            case "ap_prog_ping": return APItemProgression.GetProgressivePing(savedProgressionLevel);
            case "ap_prog_bait": return APItemProgression.GetProgressiveBait(savedProgressionLevel);
            case "ap_prog_requestBackup": return APItemProgression.GetProgressiveRequestBackup(savedProgressionLevel);
            case "ap_prog_memoryWipe": return APItemProgression.GetProgressiveMemoryWipe(savedProgressionLevel);
            case "ap_prog_sonicShock": return APItemProgression.GetProgressiveSonicShock(savedProgressionLevel);
            case "ap_prog_suicide": return APItemProgression.GetProgressiveSuicide(savedProgressionLevel);
            case "ap_prog_systemCollapse": return APItemProgression.GetProgressiveSystemCollapse(savedProgressionLevel);
            case "ap_prog_grenadeExplode": return APItemProgression.GetProgressiveDetonateGrenade(savedProgressionLevel);
            case "ap_prog_blackwallGateway": return APItemProgression.GetProgressiveBlackwallGateway(savedProgressionLevel);
            case "ap_prog_madness": return APItemProgression.GetProgressiveCyberpsychosis(savedProgressionLevel);
            
            default: return "";
        }
    }

    private static func GetProgressiveOverheat(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.OverheatLvl1Program";
            case 2: return "Items.OverheatLvl2Program";
            case 3: return "Items.OverheatLvl3Program";
            case 4: return "Items.OverheatLvl4Program";
            default: return "Items.OverheatLvl4Program"; 
        }
    }

    private static func GetProgressiveShortCircuit(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.EMPOverloadProgram";
            case 2: return "Items.EMPOverloadLvl2Program";
            case 3: return "Items.EMPOverloadLvl3Program";
            case 4: return "Items.EMPOverloadLvl4Program";
            case 5: return "Items.EMPOverloadLvl4PlusPlusProgram";
            default: return "Items.EMPLvl4Program"; 
        }
    }

    private static func GetProgressiveRebootOptics(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.BlindLvl1Program";
            case 2: return "Items.BlindLvl2Program";
            case 3: return "Items.BlindLvl3Program";
            case 4: return "Items.BlindLvl4Program";
            case 5: return "Items.BlindLvl4PlusPlusProgram";
            default: return "Items.BlindLvl4Program";
        }
    }

    private static func GetProgressiveContagion(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.ContagionProgram";             // Tier 2
            case 2: return "Items.ContagionLvl2Program";         // Tier 3
            case 3: return "Items.ContagionLvl3Program";         // Tier 4
            case 4: return "Items.ContagionLvl4Program";         // Tier 5
            case 5: return "Items.ContagionLvl4PlusPlusProgram"; // Tier 5++
            // Fallthrough protection to keep them at max tier
            default: return "Items.ContagionLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveSynapseBurnout(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.BrainMeltLvl2Program";         // Tier 3
            case 2: return "Items.BrainMeltLvl3Program";         // Tier 4
            case 3: return "Items.BrainMeltLvl4Program";         // Tier 5
            case 4: return "Items.BrainMeltLvl4PlusPlusProgram"; // Tier 5++
            
            // Keeps the player at max tier if they find extras
            default: return "Items.BrainMeltLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveCyberwareMalfunction(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.DisableCyberwareProgram";             // Tier 2
            case 2: return "Items.DisableCyberwareLvl2Program";         // Tier 3
            case 3: return "Items.DisableCyberwareLvl3Program";         // Tier 4
            case 4: return "Items.DisableCyberwareLvl4Program";         // Tier 5
            case 5: return "Items.DisableCyberwareLvl4PlusPlusProgram"; // Tier 5++
            
            default: return "Items.DisableCyberwareLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveCrippleMovement(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.LocomotionMalfunctionProgram";             // Tier 2
            case 2: return "Items.LocomotionMalfunctionLvl2Program";         // Tier 3
            case 3: return "Items.LocomotionMalfunctionLvl3Program";         // Tier 4
            case 4: return "Items.LocomotionMalfunctionLvl4Program";         // Tier 5
            case 5: return "Items.LocomotionMalfunctionLvl4PlusPlusProgram"; // Tier 5++
            
            // Standard fallthrough to max tier
            default: return "Items.LocomotionMalfunctionLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveWeaponGlitch(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.WeaponMalfunctionProgram";             // Tier 2
            case 2: return "Items.WeaponMalfunctionLvl2Program";         // Tier 3
            case 3: return "Items.WeaponMalfunctionLvl3Program";         // Tier 4
            case 4: return "Items.WeaponMalfunctionLvl4Program";         // Tier 5
            case 5: return "Items.WeaponMalfunctionLvl4PlusPlusProgram"; // Tier 5++
            
            // Safety default to max tier
            default: return "Items.WeaponMalfunctionLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressivePing(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.PingProgram";              // Tier 1
            case 2: return "Items.PingLvl2Program";          // Tier 3
            case 3: return "Items.PingLvl4Program";          // Tier 5
            case 4: return "Items.PingLvl4PlusPlusProgram";  // Tier 5++
            
            // Safety default to the highest iconic tier
            default: return "Items.PingLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveBait(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.WhistleLvl0Program";             // Tier 1
            case 2: return "Items.WhistleLvl1Program";             // Tier 2
            case 3: return "Items.WhistleLvl2Program";             // Tier 3
            case 4: return "Items.WhistleLvl3Program";             // Tier 4
            case 5: return "Items.WhistleLvl4Program";             // Tier 5
            case 6: return "Items.WhistleLvl4PlusPlusProgram";     // Tier 5++
            
            // Standard fallthrough for safety
            default: return "Items.WhistleLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveRequestBackup(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.CommsCallInLvl1Program";             // Tier 2
            case 2: return "Items.CommsCallInLvl2Program";             // Tier 3
            case 3: return "Items.CommsCallInLvl3Program";             // Tier 4
            case 4: return "Items.CommsCallInLvl4Program";             // Tier 5
            case 5: return "Items.CommsCallInLvl4PlusPlusProgram";     // Tier 5++
            
            // Standard safety fallthrough
            default: return "Items.CommsCallInLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveMemoryWipe(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.MemoryWipeLvl2Program";             // Tier 3
            case 2: return "Items.MemoryWipeLvl3Program";             // Tier 4
            case 3: return "Items.MemoryWipeLvl4Program";             // Tier 5
            case 4: return "Items.MemoryWipeLvl4PlusPlusProgram";     // Tier 5++
            
            // Safety default
            default: return "Items.MemoryWipeLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveSonicShock(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.CommsNoiseProgram";             // Tier 1
            case 2: return "Items.CommsNoiseLvl2Program";         // Tier 3
            case 3: return "Items.CommsNoiseLvl3Program";         // Tier 4
            case 4: return "Items.CommsNoiseLvl4Program";         // Tier 5
            case 5: return "Items.CommsNoiseLvl4PlusPlusProgram"; // Tier 5++
            
            // Standard safety fallthrough
            default: return "Items.CommsNoiseLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveSuicide(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.SuicideLvl3Program";             // Tier 4
            case 2: return "Items.SuicideLvl4Program";             // Tier 5
            case 3: return "Items.SuicideLvl4PlusPlusProgram";     // Tier 5++
            
            // Safety default to max tier
            default: return "Items.SuicideLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveSystemCollapse(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.SystemCollapseLvl3Program";             // Tier 4
            case 2: return "Items.SystemCollapseLvl4Program";             // Tier 5
            case 3: return "Items.SystemCollapseLvl4PlusPlusProgram";     // Tier 5++
            
            // Standard safety fallthrough
            default: return "Items.SystemCollapseLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveDetonateGrenade(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.GrenadeExplodeLvl3Program";             // Tier 4
            case 2: return "Items.GrenadeExplodeLvl4Program";             // Tier 5
            case 3: return "Items.GrenadeExplodeLvl4PlusPlusProgram";     // Tier 5++
            
            // Standard safety fallthrough
            default: return "Items.GrenadeExplodeLvl4PlusPlusProgram"; 
        }
    }

    private static func GetProgressiveBlackwallGateway(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.BlackWallProgramLvl2"; // Tier 3
            case 2: return "Items.BlackWallProgramLvl3"; // Tier 4
            case 3: return "Items.BlackWallProgramLvl4"; // Tier 5
            
            // Standard safety fallthrough
            default: return "Items.BlackWallProgramLvl4"; 
        }
    }

    private static func GetProgressiveCyberpsychosis(progressionLevel: Int32) -> String {
        switch progressionLevel {
            case 1: return "Items.MadnessLvl3Program";             // Tier 4
            case 2: return "Items.MadnessLvl4Program";             // Tier 5
            case 3: return "Items.MadnessLvl4PlusPlusProgram";     // Tier 5++
            
            // Standard safety fallthrough
            default: return "Items.MadnessLvl4PlusPlusProgram"; 
        }
    }
}