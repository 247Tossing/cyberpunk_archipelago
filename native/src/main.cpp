#include <RED4ext/RED4ext.hpp>
#include <RedLib.hpp>

// Pull in the class definition so RedLib can auto-discover it.
#include "APBridge.hpp"

// ---------------------------------------------------------------------------
// Plugin metadata – reported to RED4ext.
// ---------------------------------------------------------------------------
RED4EXT_C_EXPORT void RED4EXT_CALL GetPluginInfo(RED4ext::PluginInfo* aInfo) {
    aInfo->name    = L"CyberpunkArchipelagoPlugin";
    aInfo->author  = L"CyberpunkArchipelago";
    aInfo->version = RED4EXT_SEMVER(1, 0, 0);
    aInfo->runtime = RED4EXT_RUNTIME_LATEST;
    aInfo->sdk     = RED4EXT_SDK_LATEST;
}

// ---------------------------------------------------------------------------
// Plugin lifecycle
// ---------------------------------------------------------------------------
RED4EXT_C_EXPORT bool RED4EXT_CALL Main(RED4ext::PluginHandle aHandle,
                                        RED4ext::EMainReason   aReason,
                                        const RED4ext::Sdk*    aSdk) {
    switch (aReason) {
        case RED4ext::EMainReason::Load: {
            // RedLib discovers all RTTI_DEFINE_CLASS blocks that were linked
            // into this DLL and registers them with the game's RTTI system.
            Red::TypeInfoRegistrar::RegisterDiscovered();
            break;
        }
        case RED4ext::EMainReason::Unload: {
            // Nothing to clean up – APBridge::~APBridge() calls AP_Shutdown()
            // if still connected.
            break;
        }
    }
    return true;
}
