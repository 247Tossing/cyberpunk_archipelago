--[[
    Cyberpunk 2077 Archipelago Bridge - CET UI

    This mod provides a simple UI for connecting to the Archipelago Python bridge.

    Architecture:
    - Python client.py runs the Archipelago protocol and TCP server (localhost:51234)
    - This CET Lua script provides UI to connect the game to the Python bridge
    - TCPClient.reds handles the actual socket connection to Python bridge
    - APGameState.reds/APGameSystem.reds handle game integration

    Usage:
    1. Launch "Cyberpunk 2077 Client" from Archipelago Launcher
    2. Launch Cyberpunk 2077
    3. Open CET overlay (~) in-game
    4. Enter connection details (default: localhost:51234)
    5. Click "Connect to Archipelago"
]]

-- Connection configuration
local apConfig = {
    ip = "127.0.0.1",      -- Python bridge runs on localhost
    port = 51234,           -- Python bridge default port
    slotName = "Player1"    -- Slot name (not used, handled by Python client)
}

-- UI state
local isOverlayOpen = false

-- Track connection status from RedScript
local connectionStatus = "DISCONNECTED"
local statusMessage = "Not connected"

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
        local isActuallyConnected = apService:IsConnected()
        if isActuallyConnected then
            connectionStatus = "CONNECTED"
            statusMessage = apService:GetConnectionStatusMessage()
        else
            -- Only update to disconnected if we were previously connected
            if connectionStatus == "CONNECTED" or connectionStatus == "CONNECTING" then
                connectionStatus = "DISCONNECTED"
                statusMessage = "Not connected"
            end
        end
    end

    -- Connection status indicator
    if connectionStatus == "CONNECTED" then
        ImGui.TextColored(0.0, 1.0, 0.0, 1.0, "● CONNECTED")
    elseif connectionStatus == "CONNECTING" then
        ImGui.TextColored(1.0, 1.0, 0.0, 1.0, "● CONNECTING")
    else
        ImGui.TextColored(1.0, 0.0, 0.0, 1.0, "● DISCONNECTED")
    end

    ImGui.SameLine()
    ImGui.Text(" | " .. statusMessage)

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Instructions
    ImGui.TextWrapped("Connect to the Archipelago Python bridge running on your computer.")
    ImGui.Spacing()
    ImGui.TextWrapped("Make sure you've launched 'Cyberpunk 2077 Client' from the Archipelago Launcher first!")

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Connection settings
    ImGui.Text("Bridge Connection Settings:")
    apConfig.ip = ImGui.InputText("Server IP", apConfig.ip, 100)
    apConfig.port = ImGui.InputInt("Port", apConfig.port)

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Connect/Disconnect buttons
    if connectionStatus ~= "CONNECTED" then
        if ImGui.Button("Connect to Archipelago", 250, 35) then
            local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")

            if apService then
                local success, err = pcall(function()
                    apService:ConnectFromCET(apConfig.ip, tonumber(apConfig.port), apConfig.slotName)
                end)

                if success then
                    print("[Archipelago] Attempting to connect to Python bridge at " .. apConfig.ip .. ":" .. apConfig.port)
                    connectionStatus = "CONNECTING"
                    statusMessage = "Connecting..."
                else
                    print("[Archipelago] CET Engine Error: " .. tostring(err))
                    statusMessage = "Connection failed: " .. tostring(err)
                end
            else
                print("[Archipelago] ERROR: Could not find Archipelago.TCPClient service!")
                print("[Archipelago] Make sure the RedScript mod is installed correctly.")
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
                    print("[Archipelago] Disconnecting from Python bridge")
                    -- Status will be updated by polling, no manual update needed
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
