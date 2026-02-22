# engine/garden.py
# Garden grid engine — mycorrhizal network model. No UI here.

import random
from engine.state import GameState, GARDEN_W, GARDEN_H, GARDEN_SIZE, init_garden, plot_idx
from data import text as txt


# Plot state constants
EMPTY     = "E"
HYPHA     = "H"
NETWORK   = "N"
MATURE    = "M"
FRUITING  = "F"
DECOMP    = "X"
COMPETING = "W"

ACTIVE_STATES    = (NETWORK, MATURE, FRUITING)
LIVING_STATES    = (HYPHA, NETWORK, MATURE, FRUITING)
WATERABLE_STATES = (HYPHA, NETWORK, MATURE, FRUITING)


# ── Plot access ───────────────────────────────────────────────

def get_plot(gs: GameState, x: int, y: int) -> dict:
    return gs.garden[plot_idx(x, y)]


def set_plot(gs: GameState, x: int, y: int, **kwargs) -> None:
    p = gs.garden[plot_idx(x, y)]
    p.update(kwargs)


# ── Garden init ───────────────────────────────────────────────

def ensure_garden(gs: GameState) -> None:
    if not gs.garden_initialized or len(gs.garden) < GARDEN_SIZE:
        gs.garden = init_garden()
        gs.garden_initialized = True


# ── Actions ───────────────────────────────────────────────────

def action_inoculate(gs: GameState, x: int, y: int) -> str:
    p = get_plot(gs, x, y)
    if p["state"] != EMPTY:
        return txt.GARDEN_INOCULATE_OCCUPIED
    if gs.spores < 1:
        return txt.GARDEN_INOCULATE_NONE
    gs.spores -= 1
    set_plot(gs, x, y, state=HYPHA, age=0, fruit_age=0)
    return txt.GARDEN_INOCULATE_OK


def action_water(gs: GameState, x: int, y: int) -> str:
    p = get_plot(gs, x, y)
    if p["state"] not in WATERABLE_STATES:
        return txt.GARDEN_WATER_NONE
    if gs.water < 1:
        return txt.GARDEN_WATER_DRY
    gs.water -= 1
    new_moist = min(5, p["moisture"] + 2)
    set_plot(gs, x, y, moisture=new_moist)
    return txt.GARDEN_WATER_OK.format(moist=new_moist)


def action_clear(gs: GameState, x: int, y: int) -> str:
    p = get_plot(gs, x, y)
    if p["state"] != COMPETING:
        return txt.GARDEN_CLEAR_NONE
    set_plot(gs, x, y, state=EMPTY)
    return txt.GARDEN_CLEAR_OK


def action_enrich(gs: GameState, x: int, y: int) -> str:
    if not gs.has_compost_pile:
        return txt.GARDEN_COMPOST_NEED
    if gs.compost_level <= 0:
        return txt.GARDEN_ENRICH_NONE
    p = get_plot(gs, x, y)
    if p["state"] != EMPTY:
        return txt.GARDEN_ENRICH_NOT_EMPTY
    new_soil = min(5, p["soil"] + 2)
    set_plot(gs, x, y, soil=new_soil)
    gs.compost_level -= 1
    return txt.GARDEN_ENRICH_OK.format(soil=new_soil)


def action_add_compost(gs: GameState) -> str:
    if not gs.has_compost_pile:
        return txt.GARDEN_COMPOST_NEED
    if gs.scrap < 1:
        return txt.GARDEN_COMPOST_ADD_NONE
    gs.scrap -= 1
    gs.compost_level = min(5, gs.compost_level + 1)
    return txt.GARDEN_COMPOST_ADD_OK.format(level=gs.compost_level)


# ── Garden tick ───────────────────────────────────────────────

def garden_tick(gs: GameState) -> str | None:
    """Advance mycorrhizal network state machine, moisture, competing growth.
    Returns a flash message or None."""
    flash = None

    for i, p in enumerate(gs.garden):
        state = p["state"]
        moist = p["moisture"]
        soil  = p["soil"]
        x, y  = i % GARDEN_W, i // GARDEN_W

        # ── Moisture update ───────────────────────────────────
        if gs.weather == "rainy":
            if state in LIVING_STATES:
                if random.random() < 0.6:
                    p["moisture"] = min(5, moist + 1)
        elif moist > 0:
            loss = 2 if gs.weather in ("sunny", "windy") else 1
            p["moisture"] = max(0, moist - loss)

        moist = p["moisture"]  # re-read after weather

        # ── Skip plots that need no further processing ────────
        if state not in LIVING_STATES and state not in (DECOMP, COMPETING, EMPTY):
            continue

        # ── Age advance (living plots) ────────────────────────
        if state in LIVING_STATES:
            p["age"] += 1

        # ── Connectivity (adjacent living plots) ─────────────
        connectivity = 0
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GARDEN_W and 0 <= ny < GARDEN_H:
                if gs.garden[plot_idx(nx, ny)]["state"] in LIVING_STATES:
                    connectivity += 1

        # ── State machine transitions ─────────────────────────
        if state == HYPHA:
            if p["age"] >= 15 and connectivity >= 1 and moist > 0:
                p["state"] = NETWORK
            elif moist == 0 and random.random() < 0.15:
                p["state"] = DECOMP

        elif state == NETWORK:
            if connectivity == 0:
                p["state"] = HYPHA   # isolated — downgrade
            elif p["age"] >= 50 and connectivity >= 2 and soil >= 2:
                p["state"] = MATURE

        elif state == MATURE:
            # Check for adjacent fruiting plot (no adjacent F rule)
            adjacent_f = False
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GARDEN_W and 0 <= ny < GARDEN_H:
                    if gs.garden[plot_idx(nx, ny)]["state"] == FRUITING:
                        adjacent_f = True
                        break
            if moist >= 3 and soil >= 3 and not adjacent_f:
                if random.random() < 0.04:
                    p["state"]    = FRUITING
                    p["fruit_age"] = 0
                    # Fruiting resource gain (fires once on entering F)
                    gs.mycelium += 1
                    if random.random() < 0.30:
                        gs.water += 1
                    if random.random() < 0.10:
                        gs.power += 1
                    if not flash:
                        flash = random.choice(txt.NETWORK_FRUIT)

        elif state == FRUITING:
            p["fruit_age"] += 1
            if p["fruit_age"] >= 6:
                p["state"]    = MATURE
                p["fruit_age"] = 0

        # ── Decomposing: enrich adjacent soil ─────────────────
        if state == DECOMP:
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GARDEN_W and 0 <= ny < GARDEN_H:
                    nb = gs.garden[plot_idx(nx, ny)]
                    if nb["state"] in (HYPHA, NETWORK, MATURE):
                        if random.random() < 0.15:
                            nb["soil"] = min(5, nb["soil"] + 1)
            if random.random() < 0.10:
                p["state"] = EMPTY

        # ── Moisture flow (N/M share moisture with dry neighbors) ──
        if state in (NETWORK, MATURE) and moist >= 4:
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < GARDEN_W and 0 <= ny < GARDEN_H:
                    nb = gs.garden[plot_idx(nx, ny)]
                    if nb["state"] in LIVING_STATES and nb["moisture"] <= 1:
                        p["moisture"] -= 1
                        nb["moisture"] = min(5, nb["moisture"] + 1)
                        break  # one transfer per plot per tick

        # ── Spontaneous competing growth on empty plots ────────
        if state == EMPTY and random.random() < 0.008:
            p["state"] = COMPETING

    return flash


# ── Network summary ───────────────────────────────────────────

def network_summary(gs: GameState) -> dict:
    hypha     = sum(1 for p in gs.garden if p["state"] == HYPHA)
    connected = sum(1 for p in gs.garden if p["state"] in (NETWORK, MATURE, FRUITING))
    mature    = sum(1 for p in gs.garden if p["state"] in (MATURE, FRUITING))
    fruiting  = sum(1 for p in gs.garden if p["state"] == FRUITING)
    competing = sum(1 for p in gs.garden if p["state"] == COMPETING)
    return {
        "hypha":     hypha,
        "connected": connected,
        "mature":    mature,
        "fruiting":  fruiting,
        "competing": competing,
    }
