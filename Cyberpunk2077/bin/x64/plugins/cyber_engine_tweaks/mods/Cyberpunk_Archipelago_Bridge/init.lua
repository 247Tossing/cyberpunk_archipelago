local DEFAULTS = {
    ip = "archipelago.gg",
    port = 38281,
    slotName = "Player1"
}

local CONFIG_PATH = "config.json"
local MAX_CHAT_MESSAGES = 1000

local apConfig = {
    ip = DEFAULTS.ip,
    port = DEFAULTS.port,
    slotName = DEFAULTS.slotName
}

local isOverlayOpen = false
local connectionStatus = "DISCONNECTED"
local statusMessage = "Not connected"
local connectAttemptStartedAt = nil
local connectTimeoutSeconds = 45

local pumpAccumulator = 0.0
local pumpIntervalSeconds = 0.05

local chatMessages = {}
local syncedChatCount = 0
local chatInput = ""
local chatNeedsScroll = false

local jsonModule = nil
if type(json) == "table" then
    jsonModule = json
else
    local ok, loaded = pcall(require, "json")
    if ok and type(loaded) == "table" then
        jsonModule = loaded
    end
end

local chatColorMap = {
    default = {0.82, 0.84, 0.88, 1.0},
    black = {0.0, 0.0, 0.0, 1.0},
    red = {0.93, 0.0, 0.0, 1.0},
    green = {0.0, 1.0, 0.5, 1.0},
    yellow = {0.98, 0.98, 0.82, 1.0},
    blue = {0.39, 0.58, 0.93, 1.0},
    magenta = {0.93, 0.0, 0.93, 1.0},
    cyan = {0.0, 0.93, 0.93, 1.0},
    white = {1.0, 1.0, 1.0, 1.0},
    plum = {0.69, 0.6, 0.94, 1.0},
    slateblue = {0.43, 0.55, 0.91, 1.0},
    salmon = {0.98, 0.5, 0.45, 1.0},
    orange = {1.0, 0.47, 0.0, 1.0}
}

local function trimString(input)
    return (input:gsub("^%s*(.-)%s*$", "%1"))
end

local function parsePort(value)
    if type(value) == "number" then
        return value
    end
    if type(value) == "string" then
        return tonumber(value)
    end
    return nil
end

local function escapeJsonString(value)
    local escaped = tostring(value or "")
    escaped = escaped:gsub("\\", "\\\\")
    escaped = escaped:gsub('"', '\\"')
    escaped = escaped:gsub("\n", "\\n")
    escaped = escaped:gsub("\r", "\\r")
    return escaped
end

local function unescapeJsonString(value)
    if type(value) ~= "string" then
        return ""
    end
    local unescaped = value
    unescaped = unescaped:gsub("\\n", "\n")
    unescaped = unescaped:gsub("\\r", "\r")
    unescaped = unescaped:gsub('\\"', '"')
    unescaped = unescaped:gsub("\\\\", "\\")
    return unescaped
end

local function serializeConfig()
    return "{\n"
        .. '  "ip": "' .. escapeJsonString(apConfig.ip) .. '",\n'
        .. '  "port": ' .. tostring(tonumber(apConfig.port) or DEFAULTS.port) .. ",\n"
        .. '  "slotName": "' .. escapeJsonString(apConfig.slotName) .. '"\n'
        .. "}\n"
end

local function decodeConfig(rawText)
    if type(rawText) ~= "string" or rawText == "" then
        return nil
    end

    if jsonModule and type(jsonModule.decode) == "function" then
        local ok, parsed = pcall(function()
            return jsonModule.decode(rawText)
        end)
        if ok and type(parsed) == "table" then
            return parsed
        end
    end

    local ip = rawText:match('%"ip%"%s*:%s*%"(.-)%"')
    local port = rawText:match('%"port%"%s*:%s*(%d+)')
    local slotName = rawText:match('%"slotName%"%s*:%s*%"(.-)%"')
    if not ip or not port or not slotName then
        return nil
    end

    return {
        ip = unescapeJsonString(ip),
        port = tonumber(port),
        slotName = unescapeJsonString(slotName)
    }
end

local function loadConfig()
    local file = io.open(CONFIG_PATH, "r")
    if not file then
        return
    end

    local rawText = file:read("*a")
    file:close()

    local parsed = decodeConfig(rawText)
    if type(parsed) ~= "table" then
        return
    end

    if type(parsed.ip) == "string" and parsed.ip ~= "" then
        apConfig.ip = parsed.ip
    end
    local port = parsePort(parsed.port)
    if port and port >= 0 and port <= 65535 then
        apConfig.port = math.floor(port)
    end
    if type(parsed.slotName) == "string" and parsed.slotName ~= "" then
        apConfig.slotName = parsed.slotName
    end
end

local function saveConfig()
    local file = io.open(CONFIG_PATH, "w")
    if not file then
        print("[Archipelago] Failed to write config file: " .. CONFIG_PATH)
        return
    end

    file:write(serializeConfig())
    file:close()
end

local function decodeChatMessage(rawChatJson)
    if type(rawChatJson) ~= "string" or rawChatJson == "" then
        return nil
    end

    local parsed = nil
    if jsonModule and type(jsonModule.decode) == "function" then
        local ok, result = pcall(function()
            return jsonModule.decode(rawChatJson)
        end)
        if ok and type(result) == "table" then
            parsed = result
        end
    end

    if type(parsed) ~= "table" then
        return {
            segments = {
                { text = rawChatJson, color = "default" }
            }
        }
    end

    local message = { segments = {} }
    if type(parsed.segments) == "table" then
        for _, segment in ipairs(parsed.segments) do
            if type(segment) == "table" and type(segment.text) == "string" and segment.text ~= "" then
                table.insert(message.segments, {
                    text = segment.text,
                    color = type(segment.color) == "string" and segment.color or "default"
                })
            end
        end
    end

    if #message.segments == 0 then
        return nil
    end

    return message
end

local function appendChatMessage(rawChatJson)
    local message = decodeChatMessage(rawChatJson)
    if not message then
        return
    end

    table.insert(chatMessages, message)
    while #chatMessages > MAX_CHAT_MESSAGES do
        table.remove(chatMessages, 1)
    end
    chatNeedsScroll = true
end

local function updateConnectionStatus(apService)
    if not apService then
        return
    end

    local statusCode = 0
    local statusCodeSuccess, statusCodeResult = pcall(function()
        return apService:GetConnectionStatusCode()
    end)
    if statusCodeSuccess then
        statusCode = statusCodeResult
    end

    local statusText = ""
    local statusTextSuccess, statusTextResult = pcall(function()
        return apService:GetConnectionStatusMessage()
    end)
    if statusTextSuccess then
        statusText = statusTextResult
    end

    local lastConnectionError = ""
    local errorTextSuccess, errorTextResult = pcall(function()
        return apService:GetLastConnectionError()
    end)
    if errorTextSuccess then
        lastConnectionError = errorTextResult
    end

    local isActuallyConnected = apService:IsConnected()
    if isActuallyConnected then
        connectionStatus = "CONNECTED"
        connectAttemptStartedAt = nil
        statusMessage = statusText ~= "" and statusText or "Connected to Archipelago"
        return
    end

    if statusCode == 3 then
        connectionStatus = "DISCONNECTED"
        connectAttemptStartedAt = nil
        statusMessage = lastConnectionError ~= "" and lastConnectionError or "Connection refused"
        return
    end

    if connectionStatus == "CONNECTING" then
        if lastConnectionError ~= "" then
            connectionStatus = "DISCONNECTED"
            connectAttemptStartedAt = nil
            statusMessage = lastConnectionError
        else
            local elapsedSeconds = connectAttemptStartedAt and (os.clock() - connectAttemptStartedAt) or 0
            if elapsedSeconds >= connectTimeoutSeconds then
                connectionStatus = "DISCONNECTED"
                connectAttemptStartedAt = nil
                statusMessage = "Connection timed out. Verify host, port, and slot."
            else
                statusMessage = statusText ~= "" and statusText or "Connecting..."
            end
        end
        return
    end

    if connectionStatus == "CONNECTED" then
        connectionStatus = "DISCONNECTED"
        statusMessage = "Disconnected"
        pcall(function()
            apService:DisconnectFromCET()
        end)
    end
end

local function syncChatFromService(apService)
    if not apService then
        return
    end

    local countSuccess, chatCount = pcall(function()
        return apService:GetChatMessageCount()
    end)
    if not countSuccess or type(chatCount) ~= "number" then
        return
    end

    if chatCount < syncedChatCount then
        syncedChatCount = 0
        chatMessages = {}
    end

    for idx = syncedChatCount, chatCount - 1 do
        local messageSuccess, rawChatJson = pcall(function()
            return apService:GetChatMessageJson(idx)
        end)
        if messageSuccess and type(rawChatJson) == "string" and rawChatJson ~= "" then
            appendChatMessage(rawChatJson)
        end
    end

    syncedChatCount = chatCount
end

local function getStatusColor()
    if connectionStatus == "CONNECTED" then
        return 0.40, 0.78, 0.58, 1.0
    end
    if connectionStatus == "CONNECTING" then
        return 0.88, 0.73, 0.34, 1.0
    end
    return 0.65, 0.67, 0.72, 1.0
end

local function normalizeSegmentText(text)
    if type(text) ~= "string" then
        return ""
    end
    return text:gsub("[\r\n]+", " ")
end

local function drawChatMessage(message)
    if type(message) ~= "table" or type(message.segments) ~= "table" then
        return
    end

    local drawList = ImGui.GetWindowDrawList and ImGui.GetWindowDrawList()
    if not drawList or not ImGui.ImDrawListAddText then
        for index, segment in ipairs(message.segments) do
            local text = normalizeSegmentText(segment.text)
            if text ~= "" then
                if index > 1 then
                    ImGui.SameLine(0, 0)
                end
                local color = chatColorMap[segment.color] or chatColorMap.default
                ImGui.TextColored(color[1], color[2], color[3], color[4], text)
            end
        end
        return
    end

    local cursorX, cursorY = ImGui.GetCursorScreenPos()
    local x = cursorX
    local y = cursorY
    local lineHeight = ImGui.GetTextLineHeight()
    local fontSize = ImGui.GetFontSize()
    local maxX = cursorX + ImGui.GetContentRegionAvail()

    for _, segment in ipairs(message.segments) do
        local text = normalizeSegmentText(segment.text)
        if text ~= "" then
            local textWidth = ImGui.CalcTextSize(text)
            if x > cursorX and (x + textWidth) > maxX then
                x = cursorX
                y = y + lineHeight
            end

            local color = chatColorMap[segment.color] or chatColorMap.default
            local colorU32 = ImGui.GetColorU32(color[1], color[2], color[3], color[4])
            ImGui.ImDrawListAddText(drawList, fontSize, x, y, colorU32, text)
            x = x + textWidth
        end
    end

    local messageHeight = (y - cursorY) + lineHeight
    ImGui.Dummy(0, messageHeight)
end

registerForEvent("onOverlayOpen", function()
    isOverlayOpen = true
end)

registerForEvent("onOverlayClose", function()
    isOverlayOpen = false
end)

registerForEvent("onDraw", function()
    if not isOverlayOpen then
        return
    end

    local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
    updateConnectionStatus(apService)
    syncChatFromService(apService)

    ImGui.SetNextWindowSize(560, 520, ImGuiCond.FirstUseEver)
    ImGui.Begin("Archipelago Client")

    ImGui.PushStyleVar(ImGuiStyleVar.FramePadding, 6, 4)
    ImGui.PushStyleVar(ImGuiStyleVar.ItemSpacing, 8, 6)

    local statusR, statusG, statusB, statusA = getStatusColor()
    ImGui.TextColored(statusR, statusG, statusB, statusA, connectionStatus)
    ImGui.SameLine()
    ImGui.Text(" - " .. statusMessage)
    ImGui.Separator()

    local previousIp = apConfig.ip
    local previousPort = apConfig.port
    local previousSlot = apConfig.slotName

    ImGui.Text("Host")
    ImGui.SetNextItemWidth(-1)
    apConfig.ip = ImGui.InputText("##ArchipelagoHost", apConfig.ip, 128)

    ImGui.Text("Port")
    ImGui.SetNextItemWidth(-1)
    apConfig.port = ImGui.InputInt("##ArchipelagoPort", tonumber(apConfig.port) or DEFAULTS.port)
    if tonumber(apConfig.port) < 0 then
        apConfig.port = 0
    elseif tonumber(apConfig.port) > 65535 then
        apConfig.port = 65535
    end

    ImGui.Text("Slot")
    ImGui.SetNextItemWidth(-1)
    apConfig.slotName = ImGui.InputText("##ArchipelagoSlot", apConfig.slotName, 128)

    if previousIp ~= apConfig.ip or tonumber(previousPort) ~= tonumber(apConfig.port) or previousSlot ~= apConfig.slotName then
        saveConfig()
    end

    local buttonLabel = connectionStatus == "CONNECTED" and "Disconnect" or "Connect"
    local buttonHeight = ImGui.GetFrameHeight()
    if ImGui.Button(buttonLabel, -1, buttonHeight) then
        if not apService then
            connectionStatus = "DISCONNECTED"
            statusMessage = "RedScript service not found."
        elseif connectionStatus == "CONNECTED" then
            local success = pcall(function()
                apService:DisconnectFromCET()
            end)
            if success then
                connectionStatus = "DISCONNECTED"
                statusMessage = "Disconnected"
                syncedChatCount = 0
                chatMessages = {}
            else
                statusMessage = "Disconnect failed."
            end
        else
            local trimmedSlot = trimString(apConfig.slotName or "")
            if trimmedSlot == "" then
                connectionStatus = "DISCONNECTED"
                statusMessage = "Slot name cannot be empty."
            else
                apConfig.slotName = trimmedSlot
                saveConfig()
                local success, err = pcall(function()
                    apService:ConnectFromCET(apConfig.ip, tonumber(apConfig.port), apConfig.slotName)
                end)
                if success then
                    connectionStatus = "CONNECTING"
                    connectAttemptStartedAt = os.clock()
                    statusMessage = "Connecting..."
                    saveConfig()
                else
                    connectionStatus = "DISCONNECTED"
                    statusMessage = "Connection failed: " .. tostring(err)
                end
            end
        end
    end

    ImGui.Separator()

    local sendButtonWidth = 72
    local rowSpacing = ImGui.GetStyle().ItemSpacing.x
    local _, availY = ImGui.GetContentRegionAvail()
    local inputRowHeight = ImGui.GetFrameHeightWithSpacing()
    local chatChildHeight = availY - inputRowHeight
    if chatChildHeight < 80 then
        chatChildHeight = 80
    end
    ImGui.BeginChild("##ArchipelagoChatLog", 0, chatChildHeight, true)

    if #chatMessages == 0 then
        ImGui.TextColored(0.5, 0.52, 0.55, 1.0, "No chat yet. Messages will appear after connecting.")
    else
        for _, message in ipairs(chatMessages) do
            drawChatMessage(message)
        end
    end

    if chatNeedsScroll then
        ImGui.SetScrollHereY(1.0)
        chatNeedsScroll = false
    end

    ImGui.EndChild()

    ImGui.SetNextItemWidth(-(sendButtonWidth + rowSpacing))
    chatInput = ImGui.InputText("##ArchipelagoChatInput", chatInput, 256)
    ImGui.SameLine()
    local sendClicked = ImGui.Button("Send", sendButtonWidth, 0)
    if sendClicked and chatInput ~= "" and apService then
        local textToSend = trimString(chatInput)
        if textToSend ~= "" then
            local sent = false
            local sendSuccess = pcall(function()
                sent = apService:SendChatFromCET(textToSend)
            end)
            if sendSuccess and sent then
                chatInput = ""
            end
        end
    end

    ImGui.PopStyleVar(2)
    ImGui.End()
end)

registerForEvent("onUpdate", function(deltaTime)
    pumpAccumulator = pumpAccumulator + (deltaTime or 0)
    if pumpAccumulator < pumpIntervalSeconds then
        return
    end
    pumpAccumulator = 0.0

    local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
    if not apService then
        return
    end

    pcall(function()
        apService:Pump()
    end)
end)

registerForEvent("onInit", function()
    loadConfig()
    print("[Archipelago] Cyberpunk 2077 Archipelago Bridge loaded")
    print(string.format(
        "[Archipelago] Session config: %s:%s slot %s",
        apConfig.ip,
        tostring(apConfig.port),
        apConfig.slotName
    ))
    print("[Archipelago] Open CET overlay (~) and navigate to 'Archipelago Client' to connect")
end)

registerForEvent("onShutdown", function()
    saveConfig()
    if connectionStatus == "CONNECTED" then
        local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
        if apService then
            pcall(function()
                apService:DisconnectFromCET()
            end)
        end
    end
    print("[Archipelago] Bridge shutting down")
end)

print("[Archipelago] Archipelago Bridge module initialized")
