# engine/residents.py
# Resident system. Mood, conditions, effects, interactions.

import random
from engine.state import GameState, RESIDENT_MAX
from data import text as txt

RESIDENT_DATA = txt.RESIDENTS
INTERACTIONS  = txt.RESIDENT_INTERACTIONS
MOOD_LABELS   = txt.MOOD_LABELS


# ── Resident list helpers ─────────────────────────────────────

def resident_names(gs: GameState) -> list[str]:
    return [r["name"] for r in gs.residents]


def get_resident(gs: GameState, name: str) -> dict | None:
    for r in gs.residents:
        if r["name"] == name:
            return r
    return None


def add_resident(gs: GameState, name: str) -> bool:
    if len(gs.residents) >= RESIDENT_MAX:
        return False
    if name in resident_names(gs):
        return False
    gs.residents.append({"name": name, "mood": 2, "days": 0})
    return True


def remove_resident(gs: GameState, name: str) -> None:
    gs.residents = [r for r in gs.residents if r["name"] != name]


def pale_present(gs: GameState) -> bool:
    return "Pale" in resident_names(gs)


def community_bonus(gs: GameState) -> int:
    bonus = 0
    names = resident_names(gs)
    if "Sable"  in names: bonus += 4
    if "Thresh" in names: bonus += 2
    return bonus


# ── Condition evaluation ──────────────────────────────────────

def _primary_met(name: str, gs: GameState) -> bool:
    cond = RESIDENT_DATA[name]["primary"]
    active = gs.active_garden_plots()
    eff    = gs.panel_efficiency
    n      = len(gs.residents)
    match cond:
        case "panel_efficiency_75":  return eff >= 75
        case "panel_efficiency_50":  return eff >= 50
        case "water_or_rain":        return gs.weather == "rainy" or gs.water >= 3
        case "residents_2":          return n >= 2
        case "residents_3":          return n >= 3
        case "garden_active_2":      return active >= 2
        case "garden_active_3":      return active >= 3
        case "garden_active_5":      return active >= 5
        case "always":               return True
        case _:                      return True


def _secondary_delta(name: str, gs: GameState) -> int:
    cond  = RESIDENT_DATA[name]["secondary"]
    active = gs.active_garden_plots()
    eff    = gs.panel_efficiency
    match cond:
        case "weather_sunny":     return  1 if gs.weather == "sunny"  else 0
        case "weather_rainy":     return  1 if gs.weather == "rainy"  else 0
        case "weather_not_windy": return  1 if gs.weather != "windy"  else -1
        case "panel_efficiency_50": return 1 if eff >= 50  else -1
        case "garden_active_2":   return  1 if active >= 2 else  0
        case "weeds_low":         return  1 if gs.weedy_plots() <= 1 else -1
        case "residents_3":       return  1 if len(gs.residents) >= 3 else 0
        case "water_2":           return  1 if gs.water >= 2 else -1
        case _:                   return  0


# ── Passive effects ───────────────────────────────────────────

def _apply_effect(name: str, gs: GameState) -> str | None:
    effect = RESIDENT_DATA[name]["effect"]
    roll = random.random()
    match effect:
        case "clear_dust":
            if roll < 0.30 and gs.panel_dust:
                gs.panel_dust = False
                from engine.panel import recalc_efficiency
                recalc_efficiency(gs)
                return "the glass looks cleaner than it did."
        case "water_bonus":
            if roll < 0.20 and gs.weather == "rainy":
                gs.water += 1
                return "the ground near the rain catcher holds more than usual."
        case "soil_improve":
            if roll < 0.15 and gs.garden_initialized and gs.garden:
                idx = random.randrange(len(gs.garden))
                p = gs.garden[idx]
                if p["state"] == "E":
                    p["soil"] = min(5, p["soil"] + 1)
                    return "a corner of the garden looks different. the soil there is richer."
        case "weather_nudge":
            if roll < 0.25 and gs.weather_duration > 2:
                gs.weather_duration -= 1
        case "seed_gen":
            if roll < 0.18:
                gs.spores += 1
                return "something near the garden has yielded a little more than expected."
        case "connector_protect" | "community_draw" | "catalyst":
            pass  # handled externally
    return None


# ── Main resident tick ────────────────────────────────────────

def tick_residents(gs: GameState) -> str | None:
    """Process all residents. Returns flash text or None."""
    if not gs.residents:
        return None

    flash = None
    departing = []

    for r in gs.residents:
        name = r["name"]
        if name not in RESIDENT_DATA:
            continue

        r["days"] += 1
        primary = _primary_met(name, gs)
        delta   = _secondary_delta(name, gs)

        if primary:
            r["mood"] = min(3, r["mood"] + 1 + (1 if delta > 0 else 0))
        else:
            r["mood"] = max(0, r["mood"] - 1 + (delta if delta < 0 else 0))

        if r["mood"] == 0:
            departing.append(name)
            if not flash:
                flash = RESIDENT_DATA[name]["farewell"]
        else:
            result = _apply_effect(name, gs)
            if result and not flash:
                flash = result

    # Remove departing residents
    for name in departing:
        remove_resident(gs, name)

    # Interactions (rare)
    if len(gs.residents) >= 2 and not flash:
        if random.random() < 0.08:
            flash = _check_interactions(gs)

    return flash


def _apply_interaction_effect(pair: frozenset, gs: GameState) -> None:
    match tuple(sorted(pair)):
        case ("Tuck", "Weft"):
            gs.water += 1
        case ("Sable", "Thresh"):
            gs.mycelium += 1
        case ("Fen", "Reed"):
            if gs.garden_initialized and gs.garden:
                living = [p for p in gs.garden if p.get("state") in ("H", "N", "M", "F")]
                if living:
                    p = random.choice(living)
                    p["soil"] = min(5, p["soil"] + 1)
        case ("Pale", "Weft"):
            conditions = [c for c in ("panel_dust", "panel_wire", "panel_debris", "panel_connector")
                          if getattr(gs, c, False)]
            if conditions:
                setattr(gs, random.choice(conditions), False)
                from engine.panel import recalc_efficiency
                recalc_efficiency(gs)
        case ("Reed", "Tuck"):
            if gs.garden_initialized and gs.garden:
                living = [p for p in gs.garden if p.get("state") in ("H", "N", "M", "F")]
                if living:
                    driest = min(living, key=lambda p: p.get("moisture", 0))
                    driest["moisture"] = min(5, driest.get("moisture", 0) + 1)
        case ("Drift", "Sable"):
            gs.weather_duration = max(0, gs.weather_duration - 2)


def _check_interactions(gs: GameState) -> str | None:
    names = set(resident_names(gs))
    active = [(pair, line) for pair, line in INTERACTIONS.items() if pair.issubset(names)]
    if not active:
        return None
    random.shuffle(active)
    for pair, line in active:
        if random.random() < 0.4:
            _apply_interaction_effect(pair, gs)
            return line
    return None
