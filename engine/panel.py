# engine/panel.py
# Panel efficiency, weather, maintenance, passive generation.

import random
from engine.state import GameState
from data import text


WEATHER_STATES = ["sunny", "cloudy", "rainy", "windy"]

# Degradation probabilities per action tick
DEGRADE_PROBS = {
    "dust":      {"weather": "sunny",  "chance": 0.08},
    "wire":      {"weather": "rainy",  "chance": 0.10},
    "debris":    {"weather": "windy",  "chance": 0.09},
    "connector": {"weather": None,     "chance": 0.02},
}

CONDITIONS = ["dust", "wire", "debris", "connector"]

MAINTENANCE_COSTS = {
    "dust":      0,
    "wire":      1,
    "debris":    1,
    "connector": 1,
}


def recalc_efficiency(gs: GameState) -> None:
    eff = 100
    if gs.panel_dust:      eff -= 25
    if gs.panel_wire:      eff -= 25
    if gs.panel_debris:    eff -= 25
    if gs.panel_connector: eff -= 25
    gs.panel_efficiency = max(0, eff)


def needs_maintenance(gs: GameState) -> bool:
    return any([gs.panel_dust, gs.panel_wire,
                gs.panel_debris, gs.panel_connector])


def active_conditions(gs: GameState) -> list:
    out = []
    if gs.panel_dust:      out.append("dust")
    if gs.panel_wire:      out.append("wire")
    if gs.panel_debris:    out.append("debris")
    if gs.panel_connector: out.append("connector")
    return out


def panel_connected(gs: GameState) -> bool:
    return gs.panel_state not in ("neglected", "cleaned")


def advance_weather(gs: GameState) -> None:
    gs.weather_duration -= 1
    if gs.weather_duration <= 0:
        gs.weather = random.choice(WEATHER_STATES)
        gs.weather_duration = random.randint(6, 12)


def degrade_panel(gs: GameState, pale_present: bool = False) -> str | None:
    """Attempt to degrade a panel condition. Returns flash text or None."""
    if not panel_connected(gs):
        return None

    flash = None

    for cond, cfg in DEGRADE_PROBS.items():
        # Skip if already degraded
        if getattr(gs, f"panel_{cond}"):
            continue
        # Weather match (connector degrades in any weather)
        if cfg["weather"] and gs.weather != cfg["weather"]:
            continue
        chance = cfg["chance"]
        if cond == "connector" and pale_present:
            chance *= 0.5
        if cond == "connector" and gs.has_braced_connector:
            chance *= 0.5
        if cond == "debris" and gs.has_reinforced_mounting:
            chance *= 0.5
        if random.random() < chance:
            setattr(gs, f"panel_{cond}", True)
            recalc_efficiency(gs)
            flash = text.PANEL_FLASH[cond]
            break   # one degradation per tick

    return flash


def generate_power(gs: GameState, junction_bonus: bool = False) -> bool:
    """Passive power generation. Returns True if power was generated."""
    if not panel_connected(gs):
        return False

    eff = gs.panel_efficiency
    interval = 5
    if eff < 75: interval = 7
    if eff < 50: interval = 10
    if eff < 25: interval = 15

    if gs.action_count % interval == 0:
        gs.power += 1
        if junction_bonus and eff >= 75:
            gs.power += 1
        return True
    return False


def do_maintain(gs: GameState, condition: str) -> str:
    """Apply a maintenance action. Returns result text."""
    cost = MAINTENANCE_COSTS.get(condition, 0)
    if cost > 0 and gs.scrap < cost:
        return text.PANEL_MAINTENANCE_RESULTS[f"{condition}_no_scrap"]
    if cost > 0:
        gs.scrap -= cost
    setattr(gs, f"panel_{condition}", False)
    recalc_efficiency(gs)
    return text.PANEL_MAINTENANCE_RESULTS[condition]


def panel_description(gs: GameState) -> str:
    if gs.panel_state == "neglected":
        return text.PANEL_DESCRIPTIONS["neglected"]
    if gs.panel_state == "cleaned":
        return text.PANEL_DESCRIPTIONS["cleaned"]
    eff = gs.panel_efficiency
    for threshold in (75, 50, 25, 0):
        if eff >= threshold:
            return text.PANEL_DESCRIPTIONS[threshold]
    return text.PANEL_DESCRIPTIONS[0]


def apply_decay(gs: GameState, days: int) -> str | None:
    """Apply time-based decay to resources. Returns message or None."""
    if days <= 0:
        return None

    power_retain = 2 if gs.has_junction_box else 4

    if days >= 14:
        gs.power  = gs.power // 4
        gs.scrap  = gs.scrap // 3
        gs.water  = 0
        if gs.panel_state == "connected":
            gs.panel_state = "cleaned"
        return text.DECAY_MESSAGES["severe"]
    elif days >= 6:
        gs.power = gs.power // power_retain
        gs.water = gs.water // 2
        return text.DECAY_MESSAGES["severe"]
    elif days >= 3:
        gs.power = gs.power * 3 // (power_retain * 2)
        return text.DECAY_MESSAGES["moderate"]
    else:
        if not gs.has_junction_box:
            gs.power = max(0, gs.power - 1)
        return text.DECAY_MESSAGES["minor"]
