--[[
    Cyberpunk 2077 Archipelago Bridge - CET UI

    This mod provides a simple UI for connecting directly to an Archipelago server.

    Architecture:
    - This CET Lua script provides UI to configure connection settings
    - TCPClient.reds forwards calls into RED4ext native bindings
    - CyberpunkAP.dll embeds APCpp to connect directly to Archipelago
    - APGameState.reds/APGameSystem.reds handle game integration

    Usage:
    1. Launch Cyberpunk 2077
    2. Open CET overlay (~) in-game
    3. Enter connection details
    4. Click "Connect to Archipelago"
]]

-- Connection configuration
local apConfig = {
    ip = "127.0.0.1",
    port = 38281,
    slotName = "Player1"
}

-- UI state
local isOverlayOpen = false

-- Track connection status from RedScript
local connectionStatus = "DISCONNECTED"
local statusMessage = "Not connected"
local connectAttemptStartedAt = nil
local connectTimeoutSeconds = 45

local function trimString(input)
    return (input:gsub("^%s*(.-)%s*$", "%1"))
end

-- Keep track of when the user opens/closes the CET console
registerForEvent("onOverlayOpen", function()
    isOverlayOpen = true
end)

registerForEvent("onOverlayClose", function()
    isOverlayOpen = false
end)

-- This runs every single frame the game draws
registerForEvent("onDraw", function()
    -- Only draw our UI if the CET console is open
    if not isOverlayOpen then return end

    -- Create the Window
    ImGui.SetNextWindowSize(450, 300, ImGuiCond.FirstUseEver)
    ImGui.Begin("Archipelago Client")

    ImGui.Text("Cyberpunk 2077 Archipelago Bridge")
    ImGui.Separator()
    ImGui.Spacing()

    -- Update connection status from RedScript service
    local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
    if apService then
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
        elseif statusCode == 3 then
            connectionStatus = "DISCONNECTED"
            connectAttemptStartedAt = nil
            statusMessage = lastConnectionError ~= "" and lastConnectionError or "Connection refused"
        elseif connectionStatus == "CONNECTING" then
            if lastConnectionError ~= "" then
                connectionStatus = "DISCONNECTED"
                connectAttemptStartedAt = nil
                statusMessage = lastConnectionError
            else
                local elapsedSeconds = connectAttemptStartedAt and (os.clock() - connectAttemptStartedAt) or 0
                if elapsedSeconds >= connectTimeoutSeconds then
                    connectionStatus = "DISCONNECTED"
                    connectAttemptStartedAt = nil
                    statusMessage = "Connection timed out. Verify IP, port, and slot."
                else
                    statusMessage = statusText ~= "" and statusText or "Connecting..."
                end
            end
        else
            -- Only update to disconnected if we were previously connected.
            if connectionStatus == "CONNECTED" then
                connectionStatus = "DISCONNECTED"
                statusMessage = "Disconnected"
                -- Flush native bridge state so the next Connect press re-initializes
                -- cleanly (APBridge.Initialize early-returns if still initialized).
                pcall(function()
                    apService:DisconnectFromCET()
                end)
            end
        end
    end

    -- Connection status indicator
    if connectionStatus == "CONNECTED" then
        ImGui.TextColored(0.0, 1.0, 0.0, 1.0, "CONNECTED")
    elseif connectionStatus == "CONNECTING" then
        ImGui.TextColored(1.0, 1.0, 0.0, 1.0, "CONNECTING")
    else
        ImGui.TextColored(1.0, 0.0, 0.0, 1.0, "DISCONNECTED")
    end

    ImGui.SameLine()
    ImGui.Text(" | " .. statusMessage)

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Instructions
    ImGui.TextWrapped("Connect directly to your Archipelago server.")
    ImGui.Spacing()
    ImGui.TextWrapped("Make sure CyberpunkAP RED4ext plugin is installed and loaded.")

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Connection settings
    ImGui.Text("Bridge Connection Settings:")
    apConfig.ip = ImGui.InputText("Server IP", apConfig.ip, 100)
    apConfig.port = ImGui.InputInt("Port", apConfig.port)
    apConfig.slotName = ImGui.InputText("Slot Name", apConfig.slotName, 100)

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Connect/Disconnect buttons
    if connectionStatus ~= "CONNECTED" then
        if ImGui.Button("Connect to Archipelago", 250, 35) then
            local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")

            if apService then
                local slotName = trimString(apConfig.slotName or "")
                if slotName == "" then
                    connectionStatus = "DISCONNECTED"
                    statusMessage = "Slot name cannot be empty."
                else
                    apConfig.slotName = slotName
                    local success, err = pcall(function()
                        apService:ConnectFromCET(apConfig.ip, tonumber(apConfig.port), apConfig.slotName)
                    end)

                    if success then
                        print("[Archipelago] Attempting to connect to Archipelago at " .. apConfig.ip .. ":" .. apConfig.port .. " as " .. apConfig.slotName)
                        connectionStatus = "CONNECTING"
                        connectAttemptStartedAt = os.clock()
                        statusMessage = "Connecting..."
                    else
                        print("[Archipelago] CET Engine Error: " .. tostring(err))
                        connectionStatus = "DISCONNECTED"
                        connectAttemptStartedAt = nil
                        statusMessage = "Connection failed: " .. tostring(err)
                    end
                end
            else
                print("[Archipelago] ERROR: Could not find Archipelago.TCPClient service!")
                print("[Archipelago] Make sure the RedScript mod is installed correctly.")
                connectionStatus = "DISCONNECTED"
                connectAttemptStartedAt = nil
                statusMessage = "RedScript mod not found!"
            end
        end
    else
        if ImGui.Button("Disconnect", 250, 35) then
            local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")

            if apService then
                local success, err = pcall(function()
                    apService:DisconnectFromCET()
                end)

                if success then
                    print("[Archipelago] Disconnecting from Archipelago")
                    connectionStatus = "DISCONNECTED"
                    connectAttemptStartedAt = nil
                    statusMessage = "Disconnected"
                else
                    print("[Archipelago] CET Engine Error: " .. tostring(err))
                end
            end
        end
    end

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Help text
    ImGui.TextWrapped("Need help? Check the mod documentation or Archipelago Discord.")

    ImGui.End()
end)

-- Drain the Archipelago item/deathlink queue every frame regardless of overlay state.
-- onUpdate fires whenever the game is running, so polling continues while the player
-- is in-game with the CET console closed.
local pumpAccumulator = 0.0
local pumpIntervalSeconds = 0.05 -- ~20 Hz; cheap when idle but plenty responsive

registerForEvent("onUpdate", function(deltaTime)
    pumpAccumulator = pumpAccumulator + (deltaTime or 0)
    if pumpAccumulator < pumpIntervalSeconds then return end
    pumpAccumulator = 0.0

    local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
    if not apService then return end

    pcall(function()
        apService:Pump()
    end)
end)

-- Initialization
registerForEvent("onInit", function()
    print("[Archipelago] Cyberpunk 2077 Archipelago Bridge loaded")
    print("[Archipelago] Open CET overlay (~) and navigate to 'Archipelago Client' to connect")
end)

registerForEvent("onShutdown", function()
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
