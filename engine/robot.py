# engine/robot.py
# Tending frame — passive garden automation. No UI here.

import random
from engine.state import GameState, GARDEN_W
from engine.garden import action_harvest, action_clear_weeds, action_water
from engine.garden import READY, WEEDY, DUG, PLANTED, GROWING
from data import text as txt


TASK_ORDER = ["harvest", "clear", "water"]

TASK_LABELS = {
    "harvest": "harvest ready plots",
    "clear":   "clear weeds",
    "water":   "water dry plots",
}


def apply_frame(gs: GameState) -> str | None:
    """Apply one frame action per call. Returns flavor text or None."""
    if not gs.garden_initialized or not gs.garden:
        return None

    for task in TASK_ORDER:
        if task not in gs.frame_rules:
            continue
        for i, p in enumerate(gs.garden):
            x, y = i % GARDEN_W, i // GARDEN_W
            result = _try_task(gs, task, p, x, y)
            if result:
                return result

    return None


def _try_task(gs: GameState, task: str, p: dict, x: int, y: int) -> str | None:
    if task == "harvest" and p["state"] == READY:
        action_harvest(gs, x, y)
        return random.choice(txt.FRAME_HARVEST)

    if task == "clear" and p["state"] == WEEDY:
        action_clear_weeds(gs, x, y)
        return random.choice(txt.FRAME_CLEAR)

    if (task == "water"
            and p["state"] in (DUG, PLANTED, GROWING)
            and p["moisture"] == 0
            and gs.water > 0):
        action_water(gs, x, y)
        return random.choice(txt.FRAME_WATER)

    return None
