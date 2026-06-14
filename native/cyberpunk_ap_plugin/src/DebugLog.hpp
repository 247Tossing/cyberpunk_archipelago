#pragma once

#include <chrono>
#include <fstream>
#include <string>

namespace CyberpunkArchipelago
{
inline std::string EscapeJson(const std::string& value)
{
    std::string escaped;
    escaped.reserve(value.size() + 8);
    for (const char ch : value)
    {
        switch (ch)
        {
        case '\\':
            escaped += "\\\\";
            break;
        case '"':
            escaped += "\\\"";
            break;
        case '\n':
            escaped += "\\n";
            break;
        case '\r':
            escaped += "\\r";
            break;
        case '\t':
            escaped += "\\t";
            break;
        default:
            escaped.push_back(ch);
            break;
        }
    }
    return escaped;
}

inline void DebugLog(const std::string& runId,
                     const std::string& hypothesisId,
                     const std::string& location,
                     const std::string& message,
                     const std::string& dataJsonObject)
{
    const auto now = std::chrono::time_point_cast<std::chrono::milliseconds>(
                         std::chrono::system_clock::now())
                         .time_since_epoch()
                         .count();

    std::ofstream out("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/debug-37257d.log",
                      std::ios::app);
    if (!out.is_open())
    {
        return;
    }

    out << "{\"sessionId\":\"37257d\",\"runId\":\"" << EscapeJson(runId)
        << "\",\"hypothesisId\":\"" << EscapeJson(hypothesisId) << "\",\"location\":\""
        << EscapeJson(location) << "\",\"message\":\"" << EscapeJson(message) << "\",\"data\":"
        << dataJsonObject << ",\"timestamp\":" << now << "}\n";
}
} // namespace CyberpunkArchipelago
