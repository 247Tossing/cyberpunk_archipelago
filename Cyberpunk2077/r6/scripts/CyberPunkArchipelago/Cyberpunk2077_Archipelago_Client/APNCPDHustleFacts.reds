module Archipelago

// Fact listener registration for NCPD Organized Crime hustles that may not emit
// reliable journal UI notifications.
public class APNCPDHustleFacts {

    // Organized Crime completion facts are not consistently documented publicly.
    // We register common completion suffixes used in questphase graphs.
    private static func RegisterFactVariants(
        questSystem: ref<QuestsSystem>,
        listener: ref<IScriptable>,
        factBase: String,
        callbackName: CName
    ) -> Void {
        if StrLen(factBase) == 0 {
            return;
        }

        questSystem.RegisterListener(StringToName(s"\(factBase)_finished"), listener, callbackName);
        questSystem.RegisterListener(StringToName(s"\(factBase)_done"), listener, callbackName);
        questSystem.RegisterListener(StringToName(s"\(factBase)_complete"), listener, callbackName);
        questSystem.RegisterListener(StringToName(s"\(factBase)_completed"), listener, callbackName);
    }

    private static func RegisterOrganizedCrime(
        questSystem: ref<QuestsSystem>,
        listener: ref<IScriptable>,
        locationId: String,
        callbackName: CName
    ) -> Void {
        APNCPDHustleFacts.RegisterFactVariants(questSystem, listener, locationId, callbackName);
    }

    public static func RegisterOrganizedCrimeListeners(questSystem: ref<QuestsSystem>, listener: ref<IScriptable>) -> Void {
        if !IsDefined(questSystem) || !IsDefined(listener) {
            return;
        }

        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_hey_gle_02", n"HandleNCPDHustleHeyGle02");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_hey_spr_11", n"HandleNCPDHustleHeySpr11");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_pac_cvi_12", n"HandleNCPDHustlePacCvi12");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_wat_lch_01", n"HandleNCPDHustleWatLch01");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_wat_lch_08", n"HandleNCPDHustleWatLch08");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_wat_nid_01", n"HandleNCPDHustleWatNid01");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_wat_nid_02", n"HandleNCPDHustleWatNid02");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_wat_nid_06", n"HandleNCPDHustleWatNid06");
        APNCPDHustleFacts.RegisterOrganizedCrime(questSystem, listener, "ma_wbr_nok_05", n"HandleNCPDHustleWbrNok05");
    }
}
