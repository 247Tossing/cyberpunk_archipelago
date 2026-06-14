#include <RED4ext/RED4ext.hpp>

#include "APBridge.hpp"
#include "RedscriptAPI.hpp"

RED4EXT_C_EXPORT bool RED4EXT_CALL Main(RED4ext::v1::PluginHandle aHandle,
                                        RED4ext::v1::EMainReason aReason,
                                        const RED4ext::v1::Sdk* aSdk)
{
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
}

RED4EXT_C_EXPORT uint32_t RED4EXT_CALL Supports()
{
    return RED4EXT_API_VERSION_1;
}
