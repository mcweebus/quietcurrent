# engine/robot.py
# Tending frame — passive garden automation. No UI here.

import random
from engine.state import GameState, GARDEN_W, GARDEN_H
from engine.garden import (
    action_inoculate, action_clear, action_water,
    EMPTY, COMPETING, HYPHA, NETWORK, MATURE, FRUITING,
    ACTIVE_STATES,
)
from engine.state import plot_idx
from data import text as txt


TASK_ORDER = ["inoculate", "clear", "water"]

TASK_LABELS = {
    "inoculate": "inoculate empty plots",
    "clear":     "clear competing growth",
    "water":     "water dry plots",
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
    if task == "inoculate" and p["state"] == EMPTY and gs.spores > 0:
        # Only inoculate if adjacent to an active plot
        has_neighbor = False
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GARDEN_W and 0 <= ny < GARDEN_H:
                if gs.garden[plot_idx(nx, ny)]["state"] in ACTIVE_STATES + (HYPHA,):
                    has_neighbor = True
                    break
        if has_neighbor:
            action_inoculate(gs, x, y)
            return random.choice(txt.FRAME_INOCULATE)

    if task == "clear" and p["state"] == COMPETING:
        action_clear(gs, x, y)
        return random.choice(txt.FRAME_CLEAR)

    if (task == "water"
            and p["state"] in (HYPHA, NETWORK, MATURE, FRUITING)
            and p["moisture"] == 0
            and gs.water > 0):
        action_water(gs, x, y)
        return random.choice(txt.FRAME_WATER)

    return None
