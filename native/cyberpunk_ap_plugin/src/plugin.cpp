#include <RED4ext/RED4ext.hpp>
#include <Windows.h>
#include <fstream>
#include <string>

#include "APBridge.hpp"
#include "DebugLog.hpp"
#include "RedscriptAPI.hpp"

namespace
{
std::string GetModulePath()
{
    HMODULE module = nullptr;
    char path[MAX_PATH] = {};
    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                                GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            reinterpret_cast<LPCSTR>(&GetModulePath),
                            &module))
    {
        return "";
    }

    const DWORD len = GetModuleFileNameA(module, path, MAX_PATH);
    if (len == 0 || len >= MAX_PATH)
    {
        return "";
    }
    return std::string(path, len);
}

std::string GetWorkingDir()
{
    char cwd[MAX_PATH] = {};
    const DWORD len = GetCurrentDirectoryA(MAX_PATH, cwd);
    if (len == 0 || len >= MAX_PATH)
    {
        return "";
    }
    return std::string(cwd, len);
}

void AppendBeacon(const std::string& line)
{
    for (const char* path : {"C:/Users/Public/cyberpunkap_beacon_37257d.txt",
                             "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/cyberpunkap_beacon_37257d.txt"})
    {
        std::ofstream out(path, std::ios::app);
        if (out.is_open())
        {
            out << line << "\n";
        }
    }
}
} // namespace

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
            ",\"sdkPresent\":" + (aSdk ? "true" : "false") +
            ",\"modulePath\":\"" + CyberpunkArchipelago::EscapeJson(GetModulePath()) +
            "\",\"cwd\":\"" + CyberpunkArchipelago::EscapeJson(GetWorkingDir()) + "\"}");
    // #endregion
    // #region agent log
    AppendBeacon(std::string("{\"sessionId\":\"37257d\",\"runId\":\"startup-check\",\"hypothesisId\":\"H6\",") +
        "\"location\":\"plugin.cpp:Main:beacon\",\"message\":\"Main beacon written\",\"data\":{\"reason\":" +
        std::to_string(static_cast<int>(aReason)) + "}}");
    // #endregion

    if (aSdk && aSdk->logger)
    {
        const std::string sdkLine = std::string("CyberpunkArchipelago debug Main reason=") +
            std::to_string(static_cast<int>(aReason)) + " module=" + GetModulePath() +
            " cwd=" + GetWorkingDir();
        aSdk->logger->Info(aHandle, sdkLine.c_str());
    }

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
                                   std::string("{\"pluginName\":\"CyberpunkArchipelago\",\"version\":\"1.0.0\"") +
                                       ",\"modulePath\":\"" +
                                       CyberpunkArchipelago::EscapeJson(GetModulePath()) +
                                       "\",\"cwd\":\"" +
                                       CyberpunkArchipelago::EscapeJson(GetWorkingDir()) + "\"}");
    // #endregion
    // #region agent log
    AppendBeacon(std::string("{\"sessionId\":\"37257d\",\"runId\":\"startup-check\",\"hypothesisId\":\"H6\",") +
        "\"location\":\"plugin.cpp:Query:beacon\",\"message\":\"Query beacon written\",\"data\":{}}");
    // #endregion
}

RED4EXT_C_EXPORT uint32_t RED4EXT_CALL Supports()
{
    return RED4EXT_API_VERSION_1;
}
