#include "RedscriptAPI.hpp"

#include <string>

#include <RED4ext/Scripting/Functions.hpp>
#include <RED4ext/Scripting/Utils.hpp>

#include "APBridge.hpp"

namespace
{
RED4ext::v1::PluginHandle g_pluginHandle{0};
const RED4ext::v1::Sdk* g_sdk{nullptr};

void APInitialize(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    RED4ext::CString server;
    RED4ext::CString game;
    RED4ext::CString slot;
    RED4ext::CString password;
    RED4ext::GetParameter(aFrame, &server);
    RED4ext::GetParameter(aFrame, &game);
    RED4ext::GetParameter(aFrame, &slot);
    RED4ext::GetParameter(aFrame, &password);
    aFrame->code++;

    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().Initialize(
        server.c_str(),
        game.c_str(),
        slot.c_str(),
        password.c_str());
    }
}

void APConnect(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().Connect();
    }
}

void APDisconnect(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, void*, int64_t)
{
    aFrame->code++;
    CyberpunkArchipelago::APBridge::Get().Shutdown();
}

void APIsConnected(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().IsConnected();
    }
}

void APGetConnectionStatus(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, int32_t* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetConnectionStatus();
    }
}

void APGetLastConnectionError(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, RED4ext::CString* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        RED4ext::CString result(CyberpunkArchipelago::APBridge::Get().GetLastConnectionError().c_str());
        *aOut = result;
    }
}

void APSendLocationCheck(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    int64_t locationId = -1;
    RED4ext::GetParameter(aFrame, &locationId);
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().SendLocationCheck(locationId);
    }
}

void APSendDeathLink(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    RED4ext::CString cause;
    RED4ext::GetParameter(aFrame, &cause);
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().SendDeathLink(cause.c_str());
    }
}

void APSay(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    RED4ext::CString text;
    RED4ext::GetParameter(aFrame, &text);
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().SendSay(text.c_str());
    }
}

void APStoryComplete(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().StoryComplete();
    }
}

void APIsDeathLinkPending(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().IsDeathLinkPending();
    }
}

void APClearDeathLink(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, void*, int64_t)
{
    aFrame->code++;
    CyberpunkArchipelago::APBridge::Get().ClearDeathLink();
}

void APPollItemQueue(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, int64_t* aOut, int64_t)
{
    aFrame->code++;
    int64_t itemId = -1;
    if (aOut && CyberpunkArchipelago::APBridge::Get().PollReceivedItemId(itemId))
    {
        *aOut = itemId;
        return;
    }
    if (aOut)
    {
        *aOut = -1;
    }
}

void APPollChatMessage(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().PollChatMessage();
    }
}

void APGetPolledChatMessageJson(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, RED4ext::CString* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        RED4ext::CString result(CyberpunkArchipelago::APBridge::Get().GetPolledChatMessageJson().c_str());
        *aOut = result;
    }
}

void APGetPolledItemNotifySender(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, RED4ext::CString* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        RED4ext::CString result(CyberpunkArchipelago::APBridge::Get().GetPolledItemNotifySender().c_str());
        *aOut = result;
    }
}

void APGetPolledItemNotifyDisplayName(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, RED4ext::CString* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        RED4ext::CString result(CyberpunkArchipelago::APBridge::Get().GetPolledItemNotifyDisplayName().c_str());
        *aOut = result;
    }
}

void APGetPolledItemNetworkIndex(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, int32_t* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetPolledItemNetworkIndex();
    }
}

void APGetPolledItemShouldNotify(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetPolledItemShouldNotify();
    }
}

void APGetRestrictByMajorDistrict(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetRestrictByMajorDistrict();
    }
}

void APGetRestrictBySubDistrict(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetRestrictBySubDistrict();
    }
}

void APGetDistrictTokenGatedMajorMask(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, int32_t* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetDistrictTokenGatedMajorMask();
    }
}

void APGetWeaponRestrictionType(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, int32_t* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictionType();
    }
}

void APGetWeaponRestrictPistol(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictPistol();
    }
}

void APGetWeaponRestrictMelee(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictMelee();
    }
}

void APGetWeaponRestrictRifle(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictRifle();
    }
}

void APGetWeaponRestrictSniper(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictSniper();
    }
}

void APGetWeaponRestrictLmg(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictLmg();
    }
}

void APGetWeaponRestrictShotgun(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictShotgun();
    }
}

void APGetWeaponRestrictSmg(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetWeaponRestrictSmg();
    }
}

void APGetVendorSanityEnabled(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetVendorSanityEnabled();
    }
}

void APGetVendorSanityStockLine(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, RED4ext::CString* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        RED4ext::CString result(CyberpunkArchipelago::APBridge::Get().GetVendorSanityStockLine().c_str());
        *aOut = result;
    }
}

void APGetDeathLinkEnabled(RED4ext::IScriptable*, RED4ext::CStackFrame* aFrame, bool* aOut, int64_t)
{
    aFrame->code++;
    if (aOut)
    {
        *aOut = CyberpunkArchipelago::APBridge::Get().GetDeathLinkEnabled();
    }
}

template <typename TFunc>
void RegisterNative(RED4ext::CRTTISystem* rtti, const char* fullName, const char* shortName, TFunc fn)
{
    auto func = RED4ext::CGlobalFunction::Create(fullName, shortName, fn);
    RED4ext::CBaseFunction::Flags flags = {};
    flags.isNative = true;
    flags.isStatic = true;
    func->flags = flags;
    rtti->RegisterFunction(func);
}

void RegisterTypes()
{
    // Nothing to register up-front; functions are added in PostRegisterTypes once RTTI is ready.
}

void PostRegisterTypes()
{
    auto rtti = RED4ext::CRTTISystem::Get();

    if (!rtti)
    {
        return;
    }

    RegisterNative(rtti, "Archipelago.AP_Initialize", "AP_Initialize", &APInitialize);
    RegisterNative(rtti, "Archipelago.AP_Connect", "AP_Connect", &APConnect);
    RegisterNative(rtti, "Archipelago.AP_Disconnect", "AP_Disconnect", &APDisconnect);
    RegisterNative(rtti, "Archipelago.AP_IsConnected", "AP_IsConnected", &APIsConnected);
    RegisterNative(rtti, "Archipelago.AP_GetConnectionStatus", "AP_GetConnectionStatus", &APGetConnectionStatus);
    RegisterNative(rtti, "Archipelago.AP_GetLastConnectionError", "AP_GetLastConnectionError", &APGetLastConnectionError);
    RegisterNative(rtti, "Archipelago.AP_SendLocationCheck", "AP_SendLocationCheck", &APSendLocationCheck);
    RegisterNative(rtti, "Archipelago.AP_SendDeathLink", "AP_SendDeathLink", &APSendDeathLink);
    RegisterNative(rtti, "Archipelago.AP_Say", "AP_Say", &APSay);
    RegisterNative(rtti, "Archipelago.AP_StoryComplete", "AP_StoryComplete", &APStoryComplete);
    RegisterNative(rtti, "Archipelago.AP_IsDeathLinkPending", "AP_IsDeathLinkPending", &APIsDeathLinkPending);
    RegisterNative(rtti, "Archipelago.AP_ClearDeathLink", "AP_ClearDeathLink", &APClearDeathLink);
    RegisterNative(rtti, "Archipelago.AP_PollItemQueue", "AP_PollItemQueue", &APPollItemQueue);
    RegisterNative(rtti, "Archipelago.AP_PollChatMessage", "AP_PollChatMessage", &APPollChatMessage);
    RegisterNative(rtti, "Archipelago.AP_GetPolledChatMessageJson", "AP_GetPolledChatMessageJson", &APGetPolledChatMessageJson);
    RegisterNative(rtti, "Archipelago.AP_GetPolledItemNotifySender", "AP_GetPolledItemNotifySender", &APGetPolledItemNotifySender);
    RegisterNative(rtti, "Archipelago.AP_GetPolledItemNotifyDisplayName", "AP_GetPolledItemNotifyDisplayName", &APGetPolledItemNotifyDisplayName);
    RegisterNative(rtti, "Archipelago.AP_GetPolledItemNetworkIndex", "AP_GetPolledItemNetworkIndex", &APGetPolledItemNetworkIndex);
    RegisterNative(rtti, "Archipelago.AP_GetPolledItemShouldNotify", "AP_GetPolledItemShouldNotify", &APGetPolledItemShouldNotify);
    RegisterNative(rtti, "Archipelago.AP_GetRestrictByMajorDistrict", "AP_GetRestrictByMajorDistrict", &APGetRestrictByMajorDistrict);
    RegisterNative(rtti, "Archipelago.AP_GetRestrictBySubDistrict", "AP_GetRestrictBySubDistrict", &APGetRestrictBySubDistrict);
    RegisterNative(rtti, "Archipelago.AP_GetDistrictTokenGatedMajorMask", "AP_GetDistrictTokenGatedMajorMask", &APGetDistrictTokenGatedMajorMask);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictionType", "AP_GetWeaponRestrictionType", &APGetWeaponRestrictionType);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictPistol", "AP_GetWeaponRestrictPistol", &APGetWeaponRestrictPistol);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictMelee", "AP_GetWeaponRestrictMelee", &APGetWeaponRestrictMelee);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictRifle", "AP_GetWeaponRestrictRifle", &APGetWeaponRestrictRifle);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictSniper", "AP_GetWeaponRestrictSniper", &APGetWeaponRestrictSniper);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictLmg", "AP_GetWeaponRestrictLmg", &APGetWeaponRestrictLmg);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictShotgun", "AP_GetWeaponRestrictShotgun", &APGetWeaponRestrictShotgun);
    RegisterNative(rtti, "Archipelago.AP_GetWeaponRestrictSmg", "AP_GetWeaponRestrictSmg", &APGetWeaponRestrictSmg);
    RegisterNative(rtti, "Archipelago.AP_GetVendorSanityEnabled", "AP_GetVendorSanityEnabled", &APGetVendorSanityEnabled);
    RegisterNative(rtti, "Archipelago.AP_GetVendorSanityStockLine", "AP_GetVendorSanityStockLine", &APGetVendorSanityStockLine);
    RegisterNative(rtti, "Archipelago.AP_GetDeathLinkEnabled", "AP_GetDeathLinkEnabled", &APGetDeathLinkEnabled);

    if (g_sdk && g_sdk->logger)
    {
        g_sdk->logger->Info(g_pluginHandle, "CyberpunkArchipelago natives registered");
    }
}
} // namespace

namespace CyberpunkArchipelago
{
void RegisterRedscriptAPI(RED4ext::v1::PluginHandle handle, const RED4ext::v1::Sdk* sdk)
{
    g_pluginHandle = handle;
    g_sdk = sdk;

    auto rtti = RED4ext::CRTTISystem::Get();

    if (!rtti)
    {
        if (sdk && sdk->logger)
        {
            sdk->logger->Error(handle, "CyberpunkArchipelago: RTTI system unavailable on Load");
        }
        return;
    }

    rtti->AddRegisterCallback(&RegisterTypes);
    rtti->AddPostRegisterCallback(&PostRegisterTypes);

    if (sdk && sdk->logger)
    {
        sdk->logger->Info(handle, "CyberpunkArchipelago plugin loaded; awaiting RTTI registration");
    }
}
} // namespace CyberpunkArchipelago
