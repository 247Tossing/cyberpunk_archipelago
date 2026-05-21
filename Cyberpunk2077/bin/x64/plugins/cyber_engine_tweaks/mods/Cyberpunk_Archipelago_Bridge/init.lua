--[[
    Cyberpunk 2077 Archipelago Client - CET UI

    Architecture (APCpp native):
    - CyberpunkArchipelagoPlugin.dll (Red4EXT) uses APCpp to talk directly to
      the Archipelago server — no Python bridge required.
    - This CET Lua script provides the UI to enter connection details.
    - TCPClient.reds wraps APNativeClient (the Red4EXT native class).
    - APGameState / APGameSystem handle the in-game integration.

    Usage:
    1. Host or join an Archipelago room and note the server address + port.
    2. Launch Cyberpunk 2077 (no separate Python client needed).
    3. Open the CET overlay (~) in-game.
    4. Enter the server address, port, your slot name, and password (if any).
    5. Click "Connect to Archipelago".
]]

-- ---------------------------------------------------------------------------
-- Persisted connection settings (saved/loaded via CET settings.json)
-- ---------------------------------------------------------------------------
local cfg = {
    host     = "archipelago.gg",
    port     = 38281,
    slotName = "Player1",
    password = "",
}

-- ---------------------------------------------------------------------------
-- UI state
-- ---------------------------------------------------------------------------
local isOverlayOpen   = false
local connectionStatus = "DISCONNECTED"   -- "DISCONNECTED" | "CONNECTING" | "CONNECTED"
local statusMessage    = "Not connected"

-- ---------------------------------------------------------------------------
-- Overlay visibility
-- ---------------------------------------------------------------------------
registerForEvent("onOverlayOpen",  function() isOverlayOpen = true  end)
registerForEvent("onOverlayClose", function() isOverlayOpen = false end)

-- ---------------------------------------------------------------------------
-- Main draw loop
-- ---------------------------------------------------------------------------
registerForEvent("onDraw", function()
    if not isOverlayOpen then return end

    ImGui.SetNextWindowSize(480, 340, ImGuiCond.FirstUseEver)
    ImGui.Begin("Archipelago Client")

    ImGui.Text("Cyberpunk 2077 Archipelago (APCpp native)")
    ImGui.Separator()
    ImGui.Spacing()

    -- Refresh status from the RedScript service
    local svc = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
    if svc then
        if svc:IsConnected() then
            connectionStatus = "CONNECTED"
            statusMessage    = svc:GetConnectionStatusMessage()
        else
            if connectionStatus ~= "DISCONNECTED" then
                local raw = svc:GetConnectionStatusMessage()
                if raw ~= "" and raw ~= "Not connected" then
                    -- e.g. "Connecting to ..." or "Connection refused"
                    statusMessage = raw
                    connectionStatus = "CONNECTING"
                else
                    connectionStatus = "DISCONNECTED"
                    statusMessage    = "Not connected"
                end
            end
        end
    end

    -- Status indicator
    if connectionStatus == "CONNECTED" then
        ImGui.TextColored(0.0, 1.0, 0.0, 1.0, "CONNECTED")
    elseif connectionStatus == "CONNECTING" then
        ImGui.TextColored(1.0, 1.0, 0.0, 1.0, "CONNECTING...")
    else
        ImGui.TextColored(1.0, 0.0, 0.0, 1.0, "DISCONNECTED")
    end
    ImGui.SameLine()
    ImGui.Text(" | " .. statusMessage)

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Connection fields (greyed out while connected)
    local readOnly = (connectionStatus == "CONNECTED")

    if readOnly then
        ImGui.BeginDisabled()
    end

    ImGui.Text("Server Connection Settings:")
    ImGui.Spacing()

    cfg.host     = ImGui.InputText("Host",      cfg.host,     128)
    cfg.port     = ImGui.InputInt ("Port",      cfg.port)
    cfg.slotName = ImGui.InputText("Slot Name", cfg.slotName, 64)
    cfg.password = ImGui.InputText("Password",  cfg.password, 64)

    ImGui.Spacing()
    ImGui.TextWrapped("Note: Enter the Archipelago server address and port directly. " ..
                      "No Python bridge is needed.")

    if readOnly then
        ImGui.EndDisabled()
    end

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()

    -- Connect / Disconnect
    if connectionStatus ~= "CONNECTED" then
        if ImGui.Button("Connect to Archipelago", 270, 35) then
            local apSvc = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
            if apSvc then
                local ok, err = pcall(function()
                    apSvc:ConnectFromCETWithPassword(
                        cfg.host,
                        tonumber(cfg.port) or 38281,
                        cfg.slotName,
                        cfg.password
                    )
                end)
                if ok then
                    print("[Archipelago] Connecting to " .. cfg.host .. ":" .. tostring(cfg.port) ..
                          " as " .. cfg.slotName)
                    connectionStatus = "CONNECTING"
                    statusMessage    = "Connecting..."
                else
                    print("[Archipelago] Error: " .. tostring(err))
                    statusMessage = "Error: " .. tostring(err)
                end
            else
                statusMessage = "RedScript service not found – check mod install"
                print("[Archipelago] ERROR: Archipelago.TCPClient service not found.")
            end
        end
    else
        if ImGui.Button("Disconnect", 270, 35) then
            local apSvc = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
            if apSvc then
                pcall(function() apSvc:DisconnectFromCET() end)
                connectionStatus = "DISCONNECTED"
                statusMessage    = "Disconnected"
            end
        end
    end

    ImGui.Spacing()
    ImGui.Separator()
    ImGui.Spacing()
    ImGui.TextWrapped("Need help? See the README or ask in the Archipelago Discord.")

    ImGui.End()
end)

-- ---------------------------------------------------------------------------
-- Lifecycle
-- ---------------------------------------------------------------------------
registerForEvent("onInit", function()
    print("[Archipelago] APCpp native client loaded. Open the CET overlay to connect.")
end)

registerForEvent("onShutdown", function()
    local apSvc = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
    if apSvc and apSvc:IsConnected() then
        pcall(function() apSvc:DisconnectFromCET() end)
    end
    print("[Archipelago] Archipelago client shut down.")
end)
