module Archipelago

public class APDistrictEnforcer extends ScriptableSystem {
    // Your master list of safe drop zones
    private let safePoints: array<ref<APSafePosition>>;

    // ===== SCRIPTABLE SYSTEM LIFECYCLE =====

    public func OnAttach() -> Void {
        this.InitializeSafePoints();
        APLogger.LogDebug("APDistrictEnforcer initialized");
    }

    // ===== INITIALIZATION =====

    private func InitializeSafePoints() -> Void {

        // Pre-allocate array and create instances
        ArrayResize(this.safePoints, 14);
        let i: Int32 = 0;
        while i < 14 {
            this.safePoints[i] = new APSafePosition();
            i += 1;
        }

        // === SANTO DOMINGO ===
        this.safePoints[0].Init(Vector4(407.55753, -2577.8408, 172.27388, 1.0), APDistrict.SantoDomingo); // Near Badlands
        this.safePoints[1].Init(Vector4(-970.57697, -1743.779, 11.138428, 1.0), APDistrict.SantoDomingo); // Near Dogtown
        this.safePoints[2].Init(Vector4(124.37463, -658.48145, 7.4045105, 1.0), APDistrict.SantoDomingo); // Near Westbrook

        // === HEYWOOD ===
        this.safePoints[3].Init(Vector4(-1547.0868, -1382.5356, 47.627243, 1.0), APDistrict.Heywood); // Near Pacifica
        this.safePoints[4].Init(Vector4(-2392.2703, -241.45282, 13.285606, 1.0), APDistrict.Heywood); // Near City Center
        this.safePoints[5].Init(Vector4(-690.3017, -431.2089, 8.205002, 1.0), APDistrict.Heywood); // Near Santo Domingo

        // === CITY CENTER ===
        this.safePoints[6].Init(Vector4(-1380.8737, -89.414444, 31.29271, 1.0), APDistrict.CityCenter); // Center point

        // === WATSON ===
        this.safePoints[7].Init(Vector4(-1639.7678, 994.1771, 23.814354, 1.0), APDistrict.Watson); // Near City Center
        this.safePoints[8].Init(Vector4(-574.06366, 1840.8726, 36.308365, 1.0), APDistrict.Watson); // Near Westbrook

        // === WESTBROOK ===
        this.safePoints[9].Init(Vector4(189.44542, -277.48682, 6.841362, 1.0), APDistrict.Westbrook); // Near Santo Domingo

        // === PACIFICA & DOGTOWN ===
        this.safePoints[10].Init(Vector4(-2195.4106, -2196.1216, 11.872383, 1.0), APDistrict.Pacifica); // Pacifica near Dogtown
        this.safePoints[11].Init(Vector4(-1875.7725, -2462.1433, 35.482155, 1.0), APDistrict.Dogtown); // Dogtown near Pacifica

        // === BADLANDS ===
        this.safePoints[12].Init(Vector4(1480.8966, -1397.9923, 51.299736, 1.0), APDistrict.Badlands); // Near Santo Domingo
        this.safePoints[13].Init(Vector4(1815.632, 2269.3489, 180.18494, 1.0), APDistrict.Badlands); // Near Westbrook
    }

    public func GetNearestSafePoint(currentLocation: Vector4) -> Vector4 {
        let decidedPosition: Vector4 = Vector4(-1639.7678, 994.1771, 23.814354, 1.0); // Default position incase the calculation fails.
        let bestDistance: Float = -1.0; // -1 means no valid point found yet
        let gameSystem: ref<APGameSystem> = this.GetGameInstance().GetScriptableSystemsContainer().Get(n"Archipelago.APGameSystem") as APGameSystem;

        if !IsDefined(gameSystem) {
            APLogger.LogError("APDistrictEnforcer: Cannot get nearest safe point - game system not available");
            return decidedPosition;
        }

        for point in this.safePoints {
            // Only consider unlocked districts
            if gameSystem.GetDistrictUnlockStatus(this.ParseEnumToDistrictID(point.District)) {
                let distance: Float = Vector4.Distance(currentLocation, point.Position);

                // If this is the first valid point, or closer than current best
                if bestDistance < 0.0 || distance < bestDistance {
                    decidedPosition = point.Position;
                    bestDistance = distance;
                }
            }
        }

        return decidedPosition;
    }

    // ===== DISTRICT DETECTION =====

    // Get major district from game's district string
    public func GetMajorDistrict(subdistrictID: String) -> APDistrict {
        switch subdistrictID {
            
            // === WATSON ===
            case "Districts.Watson":
            case "Districts.LittleChina":
            case "Districts.Kabuki":
            case "Districts.Northside":
            case "Districts.ArasakaWaterfront":
                return APDistrict.Watson;

            // === WESTBROOK ===
            case "Districts.Westbrook":
            case "Districts.JapanTown":
            case "Districts.NorthOak":
            case "Districts.CharterHill":
                return APDistrict.Westbrook;

            // === CITY CENTER ===
            case "Districts.CityCenter":
            case "Districts.CorpoPlaza":
            case "Districts.Downtown":
                return APDistrict.CityCenter;

            // === HEYWOOD ===
            case "Districts.Heywood":
            case "Districts.WellSprings":
            case "Districts.Glen":
            case "Districts.VistaDelRey":
                return APDistrict.Heywood;

            // === SANTO DOMINGO ===
            case "Districts.SantoDomingo":
            case "Districts.Arroyo":
            case "Districts.RanchoCoronado":
                return APDistrict.SantoDomingo;

            // === PACIFICA ===
            case "Districts.Pacifica":
            case "Districts.Coastview":
            case "Districts.WestWindEstate":
                return APDistrict.Pacifica;
                
            // === DOGTOWN (Phantom Liberty) ===
            case "Districts.Dogtown":
                return APDistrict.Dogtown;

            // === BADLANDS ===
            case "Districts.Badlands":
            case "Districts.RedPeaks":
            case "Districts.RockyRidge":
            case "Districts.JacksonPlains":
            case "Districts.SouthernBadlands":
            case "Districts.NorthernBadlands":
            case "Districts.BiotechnicaFlats":
                return APDistrict.Badlands;

            default:
                
                return APDistrict.Unknown;
        }
    }

    public func ParseDistrictID(gameID: String) -> APDistrict {
        switch gameID {
            case "ap_dat_watson": 
                return APDistrict.Watson;
                
            case "ap_dat_westbrookAccessToken": 
                return APDistrict.Westbrook;
                
            case "ap_dat_city_centerAccessToken": 
                return APDistrict.CityCenter;
                
            case "ap_dat_heywoodAccessToken": 
                return APDistrict.Heywood;
                
            case "ap_dat_santoDomingoAccessToken": 
                return APDistrict.SantoDomingo;
                
            case "ap_dat_pacificaAccessToken": 
                return APDistrict.Pacifica;
                
            case "ap_dat_badlandsAccessToken": 
                return APDistrict.Badlands;
                
            case "ap_dat_dogtownAccessToken": 
                return APDistrict.Dogtown;
                
            default:
                return APDistrict.Unknown;
        }
    }

    public func ParseEnumToDistrictID(districtEnum: APDistrict) -> String {
        switch districtEnum {
            case APDistrict.Watson: 
                return "ap_dat_watson";
                
            case APDistrict.Westbrook: 
                return "ap_dat_westbrookAccessToken";
                
            case APDistrict.CityCenter: 
                return "ap_dat_city_centerAccessToken";
                
            case APDistrict.Heywood: 
                return "ap_dat_heywoodAccessToken";
                
            case APDistrict.SantoDomingo: 
                return "ap_dat_santoDomingoAccessToken";
                
            case APDistrict.Pacifica: 
                return "ap_dat_pacificaAccessToken";
                
            case APDistrict.Badlands: 
                return "ap_dat_badlandsAccessToken";
                
            case APDistrict.Dogtown: 
                return "ap_dat_dogtownAccessToken";
                
            default:
                return "unknown";
        }
    }
}

public class APSafePosition {
    public let Position: Vector4;
    public let District: APDistrict;

    public func Init(position: Vector4, district: APDistrict) -> Void {
        this.Position = position;
        this.District = district;
    }
}

enum APDistrict {
    Unknown = 0,
    Watson = 1,
    Westbrook = 2,
    CityCenter = 3,
    Heywood = 4,
    SantoDomingo = 5,
    Pacifica = 6,
    Badlands = 7,
    Dogtown = 8
}