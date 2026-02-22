# engine/world.py
# Passive ticks, wanderer arrival, ancestral milestones, decay.

import random
from engine.state import GameState
from engine import panel as pan
from engine import residents as res
from engine import garden as gdn
from data import text as txt


# ── Ancestral name ────────────────────────────────────────────

def get_ancestral_so_far(gs: GameState) -> str:
    return "".join(txt.ANCESTRAL_FRAGMENTS[:gs.ancestral_revealed])


def check_ancestral_milestone(gs: GameState) -> str | None:
    milestones = txt.ANCESTRAL_TEND_MILESTONES
    for m in milestones:
        if gs.tend_count >= m and gs.ancestral_revealed < milestones.index(m) + 1:
            gs.ancestral_revealed = milestones.index(m) + 1
            frag = get_ancestral_so_far(gs)
            return txt.ANCESTRAL_MILESTONE.format(fragment=frag)
    return None


# ── Passive tick ──────────────────────────────────────────────

class TickResult:
    __slots__ = ("panel_flash", "passive_flash", "resident_flash")
    def __init__(self):
        self.panel_flash:    str | None = None
        self.passive_flash:  str | None = None
        self.resident_flash: str | None = None


def tick_all(gs: GameState) -> TickResult:
    """Called after every player action."""
    gs.action_count += 1
    result = TickResult()

    # Weather + panel
    pan.advance_weather(gs)
    pale = res.pale_present(gs)
    result.panel_flash = pan.degrade_panel(gs, pale_present=pale)
    pan.generate_power(gs, junction_bonus=gs.has_junction_box)

    # Residents
    result.resident_flash = res.tick_residents(gs)

    # Passives
    if gs.has_rain_catcher and gs.action_count % 4 == 0:
        gs.water += 1
        result.passive_flash = txt.PASSIVE_RAIN_CATCHER

    if gs.has_garden_bed and gs.action_count % 8 == 0:
        gs.seeds += 1
        result.passive_flash = txt.PASSIVE_GARDEN_BED

    return result


# ── Wanderer system ───────────────────────────────────────────

def check_wanderer_arrival(gs: GameState) -> dict | None:
    """Returns wanderer dict if one arrives, else None."""
    if not gs.has_signal_beacon:
        return None

    threshold = 15 + gs.resident_count() * 3 + res.community_bonus(gs)
    threshold = min(45, threshold)

    if random.randint(0, 99) < threshold:
        return _spawn_wanderer(gs)
    return None


def _spawn_wanderer(gs: GameState) -> dict:
    wanderer = random.choice(txt.WANDERERS)
    gs.wanderer_count += 1
    return wanderer


def resolve_trade(gs: GameState, wanderer: dict, accept: bool) -> str:
    if not accept:
        msg = random.choice(txt.WANDERER_TRADE_DECLINE)
        return msg.format(name=wanderer["name"])

    # Check if player can pay
    want     = wanderer["want"]
    want_amt = wanderer["want_amt"]
    if getattr(gs, want) < want_amt:
        return f"you don't have enough {want}."

    setattr(gs, want,          getattr(gs, want) - want_amt)
    setattr(gs, wanderer["give"], getattr(gs, wanderer["give"]) + wanderer["give_amt"])

    msg = random.choice(txt.WANDERER_TRADE_ACCEPT)

    # Fragment reveal
    frag_line = None
    if wanderer.get("fragment") and gs.ancestral_revealed < len(txt.ANCESTRAL_FRAGMENTS):
        gs.ancestral_revealed += 1
        frag = get_ancestral_so_far(gs)
        frag_line = txt.WANDERER_FRAGMENT.format(
            name=wanderer["name"], fragment=frag
        )

    return msg + ("\n  " + frag_line if frag_line else "")


def resolve_stay(gs: GameState, wanderer: dict) -> str:
    name = wanderer["name"]
    if random.random() < wanderer["stay_chance"]:
        added = res.add_resident(gs, name)
        if added:
            return txt.WANDERER_STAY.format(name=name)
        else:
            return txt.WANDERER_NO_ROOM.format(name=name)
    return txt.WANDERER_LEAVE.format(name=name)


# ── Exploration ───────────────────────────────────────────────

def explore_die(gs: GameState) -> str | None:
    gs.power = gs.power // 2
    gs.scrap = gs.scrap // 2
    if gs.panel_state == "connected":
        gs.panel_state = "cleaned"

    frag_line = None
    if gs.ancestral_revealed < len(txt.ANCESTRAL_FRAGMENTS):
        gs.ancestral_revealed += 1
        frag = get_ancestral_so_far(gs)
        frag_line = txt.ANCESTRAL_DEATH.format(fragment=frag)

    return frag_line
