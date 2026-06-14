if PopVersion >= "0.30.4" then
    Tracker.AllowDeferredLogicUpdate = true
end

require("scripts.autotracking")

Tracker:AddItems("items/received_items.json")
Tracker:AddItems("items/location_checks.json")
Tracker:AddLayouts("layouts/tracker.json")
