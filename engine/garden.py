# engine/garden.py
# Garden grid engine. No UI here — pure state mutation.

import random
from engine.state import GameState, GARDEN_W, GARDEN_H, GARDEN_SIZE, init_garden, plot_idx
from data import text as txt


CROPS = txt.CROPS

# Plot state constants
EMPTY    = "E"
DUG      = "D"
PLANTED  = "P"
GROWING  = "G"
READY    = "R"
WEEDY    = "W"
DEPLETED = "X"

ACTIVE_STATES = (GROWING, READY)
WORKABLE_STATES = (DUG, PLANTED, GROWING)


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

def action_dig(gs: GameState, x: int, y: int) -> str:
    p = get_plot(gs, x, y)
    if p["state"] == WEEDY:
        return txt.GARDEN_DIG_WEEDS
    if p["state"] != EMPTY:
        return txt.GARDEN_DIG_DONE
    set_plot(gs, x, y, state=DUG)
    return txt.GARDEN_DIG_OK.format(soil=p["soil"])


def action_plant(gs: GameState, x: int, y: int, crop: str) -> str:
    p = get_plot(gs, x, y)
    if p["state"] != DUG:
        return txt.GARDEN_PLANT_NONE
    if gs.seeds < 1:
        return txt.GARDEN_PLANT_NOSEED
    if crop not in CROPS:
        return "unknown crop."
    gs.seeds -= 1
    set_plot(gs, x, y, state=PLANTED, crop=crop, growth=0)
    return txt.GARDEN_PLANT_OK


def action_water(gs: GameState, x: int, y: int) -> str:
    p = get_plot(gs, x, y)
    if p["state"] not in WORKABLE_STATES:
        return txt.GARDEN_WATER_NONE
    if gs.water < 1:
        return txt.GARDEN_WATER_DRY
    gs.water -= 1
    new_moist = min(5, p["moisture"] + 2)
    set_plot(gs, x, y, moisture=new_moist)
    return txt.GARDEN_WATER_OK.format(moist=new_moist)


def action_harvest(gs: GameState, x: int, y: int,
                   pollinator_bonus: bool = False) -> str:
    p = get_plot(gs, x, y)
    if p["state"] != READY:
        return txt.GARDEN_HARVEST_WAIT

    crop_key = p["crop"]
    crop = CROPS.get(crop_key, {})
    harvest = crop.get("harvest", {})
    bonus = 1 if pollinator_bonus else 0
    msg_parts = []

    for resource, (lo, hi) in harvest.items():
        amt = random.randint(lo, hi) + bonus
        setattr(gs, resource, getattr(gs, resource) + amt)
        msg_parts.append(f"+{amt} {resource}")

    soil_bonus = crop.get("soil_bonus", 0)
    if soil_bonus:
        new_soil = min(5, p["soil"] + soil_bonus)
        set_plot(gs, x, y, state=DEPLETED, crop="none", growth=0,
                 soil=new_soil)
        msg_parts.append(f"soil {new_soil}")
    else:
        set_plot(gs, x, y, state=DEPLETED, crop="none", growth=0)

    msg = f"{crop_key}. {', '.join(msg_parts)}."
    if pollinator_bonus:
        msg += f" [{txt.POLLINATOR_BONUS}]"
    return msg


def action_clear_weeds(gs: GameState, x: int, y: int) -> str:
    p = get_plot(gs, x, y)
    if p["state"] != WEEDY:
        return txt.GARDEN_WEED_NONE
    set_plot(gs, x, y, state=EMPTY)
    return txt.GARDEN_WEED_OK


def action_apply_compost(gs: GameState, x: int, y: int) -> str:
    if not gs.has_compost_pile:
        return txt.GARDEN_COMPOST_NEED
    if gs.compost_level <= 0:
        return txt.GARDEN_COMPOST_APPLY_EMPTY
    p = get_plot(gs, x, y)
    if p["state"] != DUG:
        return txt.GARDEN_COMPOST_APPLY_NODIG
    new_soil = min(5, p["soil"] + 1)
    set_plot(gs, x, y, soil=new_soil)
    gs.compost_level -= 1
    return txt.GARDEN_COMPOST_APPLY_OK.format(soil=new_soil)


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
    """Advance growth, evaporate moisture, spread weeds.
    Returns a flash message or None."""
    flash = None

    for i, p in enumerate(gs.garden):
        state = p["state"]
        moist = p["moisture"]
        soil  = p["soil"]

        # Moisture: rain waters exposed plots; sun/wind dries faster
        if gs.weather == "rainy":
            if state in (DUG, PLANTED, GROWING, READY):
                if random.random() < 0.6:
                    p["moisture"] = min(5, moist + 1)
            # no evaporation — rain compensates
        elif moist > 0:
            loss = 2 if gs.weather in ("sunny", "windy") else 1
            p["moisture"] = max(0, moist - loss)

        # Growth advance
        moist = p["moisture"]  # re-read after weather update
        if state in (PLANTED, GROWING) and moist > 0:
            rate = int(soil * 4 + moist * 2)
            p["growth"] = min(100, p["growth"] + rate)
            p["state"] = GROWING
            if p["growth"] >= 100:
                p["state"] = READY

        # Weed spread (1% per empty/dug plot per action)
        if state in (EMPTY, DUG):
            if random.random() < 0.01:
                p["state"] = WEEDY

        # Depleted recovery (8% chance per action)
        if state == DEPLETED:
            if random.random() < 0.08:
                p["state"] = EMPTY

    return flash


# ── Pollinators ───────────────────────────────────────────────

class PollinatorSystem:
    """Manages pollinator positions during a garden session.
    Not persisted — regenerates each visit."""

    def __init__(self):
        self.positions: list[tuple[int, int]] = []

    def tick(self, gs: GameState) -> None:
        active = sum(
            1 for p in gs.garden if p["state"] in ACTIVE_STATES
        )

        # Spawn if conditions met
        if len(self.positions) < 3 and active >= 2:
            spawn_chance = max(0, 6 - active)
            if random.random() < spawn_chance / 20:
                self.positions.append((
                    random.randint(0, GARDEN_W - 1),
                    random.randint(0, GARDEN_H - 1),
                ))

        # Wander + 10% leave
        new_pos = []
        for (px, py) in self.positions:
            if random.random() < 0.10:
                continue  # leaves
            dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
            px = max(0, min(GARDEN_W - 1, px + dx))
            py = max(0, min(GARDEN_H - 1, py + dy))
            new_pos.append((px, py))
        self.positions = new_pos

    def nearby(self, x: int, y: int) -> bool:
        """True if a pollinator is on or adjacent to (x, y)."""
        for (px, py) in self.positions:
            if abs(px - x) <= 1 and abs(py - y) <= 1:
                return True
        return False

    def at(self, x: int, y: int) -> bool:
        return (x, y) in self.positions


# ── Summary stats ─────────────────────────────────────────────

def garden_summary(gs: GameState) -> dict:
    total = growing = ready = weedy = 0
    for p in gs.garden:
        s = p["state"]
        if s not in (EMPTY, DEPLETED):
            total += 1
        if s == GROWING: growing += 1
        if s == READY:   ready += 1
        if s == WEEDY:   weedy += 1
    return {
        "total":   total,
        "growing": growing,
        "ready":   ready,
        "weedy":   weedy,
    }
