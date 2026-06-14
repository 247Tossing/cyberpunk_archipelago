#include <RED4ext/RED4ext.hpp>
#include <string>

#include "APBridge.hpp"
#include "DebugLog.hpp"
#include "RedscriptAPI.hpp"

RED4EXT_C_EXPORT bool RED4EXT_CALL Main(RED4ext::v1::PluginHandle aHandle,
                                        RED4ext::v1::EMainReason aReason,
                                        const RED4ext::v1::Sdk* aSdk)
{
    // #region agent log
    CyberpunkArchipelago::DebugLog(
        "startup-check",
        "H1",
        "plugin.cpp:Main",
        "Plugin Main invoked",
        std::string("{\"reason\":") + std::to_string(static_cast<int>(aReason)) +
            ",\"sdkPresent\":" + (aSdk ? "true" : "false") + "}");
    // #endregion

    switch (aReason)
    {
    case RED4ext::v1::EMainReason::Load:
        CyberpunkArchipelago::RegisterRedscriptAPI(aHandle, aSdk);
        break;
    case RED4ext::v1::EMainReason::Unload:
        CyberpunkArchipelago::APBridge::Get().Shutdown();
        break;
    }

    return true;
}

RED4EXT_C_EXPORT void RED4EXT_CALL Query(RED4ext::v1::PluginInfo* aInfo)
{
    aInfo->name = L"CyberpunkArchipelago";
    aInfo->author = L"CyberpunkArchipelagoMod";
    aInfo->version = RED4EXT_V1_SEMVER(1, 0, 0);
    aInfo->runtime = RED4EXT_V1_RUNTIME_VERSION_INDEPENDENT;
    aInfo->sdk = RED4EXT_V1_SDK_VERSION_CURRENT;

    // #region agent log
    CyberpunkArchipelago::DebugLog("startup-check",
                                   "H1",
                                   "plugin.cpp:Query",
                                   "Plugin Query invoked",
                                   "{\"pluginName\":\"CyberpunkArchipelago\",\"version\":\"1.0.0\"}");
    // #endregion
}

RED4EXT_C_EXPORT uint32_t RED4EXT_CALL Supports()
{
    return RED4EXT_API_VERSION_1;
}
