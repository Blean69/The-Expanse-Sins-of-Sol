-- Disabled native capability probe, NEVER a production salvage implementation.
-- Existing pirate notifications keep their real pirate labels. Test recipients only.
-- No rewards, research, payment, camera motion, vision grants or external clocks.
local EventMetadata = require("event_metadata")
local PROBE_ENABLED = false
local PROBE_PLAYER_INDEX = 0

function Get_event_metadata()
    local m = EventMetadata.create()
    m.event_id = "expanse18_operations_native_probe"
    m.event_version = 1.0
    m.register_event_function = "Expanse18_probe_register"
    m.on_event_registered_function = "Expanse18_probe_registered"
    m.on_initialize_function = "Expanse18_probe_initialize"
    m.should_trigger_function = "Expanse18_probe_should_trigger"
    m.on_start_function = "Expanse18_probe_start"
    m.on_update_function = "Expanse18_probe_update"
    m.on_complete_function = "Expanse18_probe_complete"
    m.on_cancel_function = "Expanse18_probe_cancel"
    m.on_teardown_function = "Expanse18_probe_teardown"
    m.trigger_check_interval_seconds = 1
    m.update_interval_seconds = 1
    m.max_concurrent_instances = 1
    return m
end

function Expanse18_probe_register(context)
    return PROBE_ENABLED
end
function Expanse18_probe_registered(context)
    -- This is documented event lifetime state, NOT a verified save/load ledger.
    context.shared.has_started = false
end
function Expanse18_probe_initialize(context)
    context.instance.phase = "uncommitted"
end
function Expanse18_probe_should_trigger(context)
    return context.shared.has_started == false and context.simulation.current_time >= 15
end
function Expanse18_probe_start(context)
    context.shared.has_started = true
    local sim = context.simulation
    local player = sim:get_player_by_player_index(PROBE_PLAYER_INDEX)
    if not player or player.is_npc or player.has_lost or not player.home_planet then
        context.instance.failure = "missing_active_test_player_home"
        return
    end
    local well_id = player.home_planet:get_gravity_well_id()
    local well = sim:get_unit_by_id(well_id)
    if not well then
        context.instance.failure = "missing_test_well"
        return
    end
    local unit = sim:spawn_unit("trader_scout_corvette", well, player)
    if not unit then
        context.instance.failure = "spawn_failed"
        return
    end
    sim:set_unit_auto_order_mode(unit, "hold_position")
    context.instance.unit_id = unit.id
    context.instance.owner_id = sim:get_unit_owner_id(unit.id)
    context.instance.well_id = well_id
    local p = sim:get_unit_position(unit)
    if not p then
        context.instance.failure = "spawn_position_unavailable"
        return
    end
    context.instance.x = p.x
    context.instance.y = p.y
    context.instance.z = p.z
    context.instance.phase = "committed"
    print("[expanse18_probe] committed player=" .. player.name .. " actual_well_id=" .. tostring(well_id) .. " unit_id=" .. tostring(unit.id))
    -- Existing global-looking native event and existing actor/well payload call.
    -- Target-player index is NOT verified as a recovery-owner field/recipient list.
    context.show_notification(NOTIFY_PIRATE_INCURSION_STARTED, {})
    context.show_notification(NOTIFY_PIRATE_KING_ARRIVED, {
        gravity_well_id = well_id, target_player_index = PROBE_PLAYER_INDEX
    })
end
function Expanse18_probe_update(context)
    local s, sim = context.instance, context.simulation
    if s.failure then
        context.cancel()
        return
    end
    local unit = sim:get_unit_by_id(s.unit_id)
    local player = sim:get_player_by_player_index(PROBE_PLAYER_INDEX)
    if not unit or not sim:does_unit_exist(unit) then
        s.failure = "tracked_object_lost"
    elseif not player or player.has_lost then
        s.failure = "owner_defeated"
    elseif sim:get_unit_owner_id(s.unit_id) ~= s.owner_id then
        s.failure = "ownership_changed"
    elseif sim:get_unit_current_gravity_well_id(s.unit_id) ~= s.well_id then
        s.failure = "left_gravity_well"
    else
        local p = sim:get_unit_position(unit)
        if not p then
            s.failure = "position_unavailable"
        elseif (p.x-s.x)^2 + (p.y-s.y)^2 + (p.z-s.z)^2 > 2500^2 then
            s.failure = "left_2500_range"
        end
    end
    if s.failure then
        context.cancel()
    elseif context.elapsed_time >= 90 then
        context.complete()
    end
end
function Expanse18_probe_complete(context)
    context.instance.phase = "completed"
    print("[expanse18_probe] completed (NO REWARD) unit_id=" .. tostring(context.instance.unit_id))
    context.show_notification(NOTIFY_PIRATE_INCURSION_ENDED, {target_player_index = PROBE_PLAYER_INDEX})
end
function Expanse18_probe_cancel(context)
    context.instance.phase = "interrupted"
    print("[expanse18_probe] interrupted reason=" .. tostring(context.instance.failure) .. " (NO REWARD)")
    if context.instance.unit_id then
        context.show_notification(NOTIFY_PIRATE_INCURSION_ENDED, {target_player_index = PROBE_PLAYER_INDEX})
    end
end
function Expanse18_probe_teardown(context)
    -- Leave the test scout present: no scuttling/capture/destruction side effects.
    -- Timer/status persistence and historical-alert replay must be engine-tested.
end
