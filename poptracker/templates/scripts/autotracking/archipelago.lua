require("scripts.autotracking.item_mapping")
require("scripts.autotracking.location_mapping")

local CUR_INDEX = -1

local function debug_log(message)
    if AUTOTRACKER_ENABLE_DEBUG_LOGGING_AP then
        print(message)
    end
end

local function reset_item(code, item_type)
    local obj = Tracker:FindObjectForCode(code)
    if not obj then
        debug_log(string.format("onClear: could not find item object for code %s", code))
        return
    end

    if item_type == "toggle" then
        obj.Active = false
    elseif item_type == "progressive" then
        obj.CurrentStage = 0
        obj.Active = false
    elseif item_type == "consumable" then
        obj.AcquiredCount = 0
    else
        debug_log(string.format("onClear: unknown item type %s for code %s", item_type, code))
    end
end

local function collect_item(code, item_type, multiplier)
    local obj = Tracker:FindObjectForCode(code)
    if not obj then
        debug_log(string.format("onItem: could not find item object for code %s", code))
        return
    end

    if item_type == "toggle" then
        obj.Active = true
    elseif item_type == "progressive" then
        if obj.Active then
            obj.CurrentStage = obj.CurrentStage + 1
        else
            obj.Active = true
        end
    elseif item_type == "consumable" then
        local amount = multiplier or 1
        obj.AcquiredCount = obj.AcquiredCount + (obj.Increment * amount)
        if obj.MaxCount >= obj.MinCount and obj.AcquiredCount > obj.MaxCount then
            obj.AcquiredCount = obj.MaxCount
        end
    else
        debug_log(string.format("onItem: unknown item type %s for code %s", item_type, code))
    end
end

local function on_clear(slot_data)
    debug_log("called onClear")
    CUR_INDEX = -1

    for _, mapping in pairs(ITEM_MAPPING) do
        if mapping[1] and mapping[2] then
            reset_item(mapping[1], mapping[2])
        end
    end

    for _, mapping in pairs(LOCATION_MAPPING) do
        for _, code in pairs(mapping) do
            local obj = Tracker:FindObjectForCode(code)
            if obj then
                obj.Active = false
            else
                debug_log(string.format("onClear: could not find location object for code %s", code))
            end
        end
    end
end

local function on_item(index, item_id, item_name, player_number)
    if not AUTOTRACKER_ENABLE_ITEM_TRACKING then
        return
    end
    if index <= CUR_INDEX then
        return
    end
    CUR_INDEX = index

    local mapping = ITEM_MAPPING[item_id]
    if not mapping then
        debug_log(string.format("onItem: no mapping for item id %s", item_id))
        return
    end

    collect_item(mapping[1], mapping[2], mapping[3])
end

local function on_location(location_id, location_name)
    if not AUTOTRACKER_ENABLE_LOCATION_TRACKING then
        return
    end

    local mapping = LOCATION_MAPPING[location_id]
    if not mapping then
        debug_log(string.format("onLocation: no mapping for location id %s", location_id))
        return
    end

    for _, code in pairs(mapping) do
        local obj = Tracker:FindObjectForCode(code)
        if obj then
            obj.Active = true
        else
            debug_log(string.format("onLocation: could not find location object for code %s", code))
        end
    end
end

Archipelago:AddClearHandler("clear handler", on_clear)
Archipelago:AddItemHandler("item handler", on_item)
Archipelago:AddLocationHandler("location handler", on_location)
