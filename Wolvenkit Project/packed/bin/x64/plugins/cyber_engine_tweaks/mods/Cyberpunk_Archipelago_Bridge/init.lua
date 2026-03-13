-- Store the configuration in a local Lua table
local apConfig = {
    ip = "127.0.0.1", -- This 
    port = 38281,
    slotName = "CHANGE_ME"
}

local isOverlayOpen = false

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

    -- 1. Create the Window
    ImGui.Begin("Archipelago Client")

    -- 2. Create the Input Fields (ImGui automatically updates our apConfig table)
    apConfig.ip = ImGui.InputText("Cyberpunk APClient IP (Probably Localhost or 127.0.0.1)", apConfig.ip, 100)
    apConfig.port = ImGui.InputInt("Port (Check the Cyberpunk APClient Logs for the correct port)", apConfig.port)
    apConfig.slotName = ImGui.InputText("Slot Name", apConfig.slotName, 100)

    ImGui.Spacing()

    -- 3. Create the Connect Button
if ImGui.Button("Connect to Archipelago") then
        local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
        
        if apService then            
            local success, err = pcall(function()
                apService:ConnectFromCET(apConfig.ip, tonumber(apConfig.port), apConfig.slotName)
            end)
            
            if success then
                print("Attepmting to connect to Cyberpunk TCP Server")
            else
                print("CET Engine Error: " .. tostring(err))
            end
        else
            print("CET Error: Could not find Archipelago.TCPClient")
        end
    end

    -- 4. End the Window
    ImGui.End()

if ImGui.Button("Disconnect") then
        local apService = Game.GetScriptableServiceContainer():GetService("Archipelago.TCPClient")
        
        if apService then
            -- pcall acts like a try/catch block for the REDengine bridge
            local success, err = pcall(function()
                apService:DisconnectFromCET()
            end)
            
            if success then
                print("Disconnecting from Cyberpunk TCP Server")
            else
                print("CET Engine Error: " .. tostring(err))
            end
        else
            print("CET Error: Could not find Archipelago.TCPClient")
        end
    end

    -- 4. End the Window
    ImGui.End()

end)