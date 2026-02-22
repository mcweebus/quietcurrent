# engine/flowers.py
# Flower garden engine. No UI imports — pure state mutation.

import random
from engine.state import GameState
from data import text as txt


# --- Slot geometry ---
# Each entry: (ring, row_off, col_off)
# Screen formula: screen_row = center_row + row_off
#                 screen_col = center_col + col_off * 2
# col_off steps by 2 so horizontal spacing = vertical spacing on terminal.

FLOWER_SLOTS = [
    (0,  0,  0),                            # 0 — center
    (1, -1,  0), (1,  1,  0),              # 1–2 — ring 1 vertical
    (1,  0, -2), (1,  0,  2),              # 3–4 — ring 1 horizontal
    (2, -2,  0), (2,  2,  0),              # 5–6 — ring 2 vertical
    (2,  0, -4), (2,  0,  4),              # 7–8 — ring 2 horizontal
    (2, -1, -2), (2, -1,  2),              # 9–10 — ring 2 upper diagonals
    (2,  1, -2), (2,  1,  2),              # 11–12 — ring 2 lower diagonals
]
FLOWER_SLOT_COUNT = len(FLOWER_SLOTS)

# Lookup tables built at module load
_SLOT_POS = {i: (ro, co) for i, (_, ro, co) in enumerate(FLOWER_SLOTS)}
_POS_IDX  = {(ro, co): i for i, (_, ro, co) in enumerate(FLOWER_SLOTS)}

# Adjacency offsets in (row_delta, col_delta) space — col steps are 2
_NEIGHBOR_OFFSETS = [(-1, 0), (1, 0), (0, -2), (0, 2),
                     (-1, -2), (-1, 2), (1, -2), (1, 2)]


def _build_neighbors() -> dict:
    result = {}
    for i in range(FLOWER_SLOT_COUNT):
        ro, co = _SLOT_POS[i]
        nbrs = []
        for dr, dc in _NEIGHBOR_OFFSETS:
            pos = (ro + dr, co + dc)
            if pos in _POS_IDX:
                nbrs.append(_POS_IDX[pos])
        result[i] = nbrs
    return result


SLOT_NEIGHBORS = _build_neighbors()


# --- Flower varieties ---
# bloom_sym: single ASCII character — safe in all terminals, single-column width.
# color: integer pair ID matching ui/screen.py constants — no UI import needed.
_C_DIM          = 1
_C_MAGENTA      = 7
_C_BRIGHT_GREEN = 10
_C_BRIGHT_YELLOW = 11
_C_BRIGHT_CYAN  = 12

FLOWERS = {
    "marigold": {
        "label":       "marigold",
        "bloom_sym":   "*",
        "color":       _C_BRIGHT_YELLOW,
        "speed":       1.2,      # age points per tick while budding
        "seed_chance": 0.04,     # chance per tick to seed a neighbor while flowering
        "bloom_life":  180,      # ticks before wilting
        "desc":        "bright and fast. seeds readily.",
    },
    "lavender": {
        "label":       "lavender",
        "bloom_sym":   "^",
        "color":       _C_MAGENTA,
        "speed":       0.6,
        "seed_chance": 0.01,
        "bloom_life":  350,
        "desc":        "slow to open. holds a long while.",
    },
    "clover": {
        "label":       "clover",
        "bloom_sym":   "+",
        "color":       _C_BRIGHT_GREEN,
        "speed":       1.8,
        "seed_chance": 0.06,
        "bloom_life":  120,
        "desc":        "low and spreading. volunteers everywhere.",
    },
    "moonflower": {
        "label":       "moonflower",
        "bloom_sym":   "o",
        "color":       _C_BRIGHT_CYAN,
        "speed":       0.4,
        "seed_chance": 0.005,
        "bloom_life":  500,
        "desc":        "rare. unhurried. blooms in its own time.",
    },
}


# --- Garden initialisation ---

def init_flowers() -> list:
    return [{"state": "E", "flower": "none", "age": 0}
            for _ in range(FLOWER_SLOT_COUNT)]


def ensure_flower_garden(gs: GameState) -> None:
    if len(gs.flowers) < FLOWER_SLOT_COUNT:
        gs.flowers = init_flowers()


# --- Actions ---

def action_plant_flower(gs: GameState, idx: int, flower_key: str) -> str:
    """Plant a flower in an empty slot. No resource cost."""
    slot = gs.flowers[idx]
    if slot["state"] != "E":
        return txt.FLOWER_PLANT_OCCUPIED
    if flower_key not in FLOWERS:
        return "unknown flower."
    slot["state"]  = "B"
    slot["flower"] = flower_key
    slot["age"]    = 0
    return txt.FLOWER_PLANTED.format(flower=FLOWERS[flower_key]["label"])


# --- Tick ---

def flower_tick(gs: GameState) -> None:
    """Advance all flower slots. Call after each player action in the view."""
    seeds_to_plant = []   # (target_idx, flower_key) — applied after iteration

    for i, slot in enumerate(gs.flowers):
        state  = slot["state"]
        flower = slot["flower"]
        spec   = FLOWERS.get(flower, {})

        if state == "B":
            # Budding → grow toward flowering
            slot["age"] += spec.get("speed", 1.0)
            if slot["age"] >= 100:
                slot["state"] = "F"
                slot["age"]   = 0

        elif state == "F":
            # Flowering — count bloom ticks, attempt self-seeding
            slot["age"] += 1
            if random.random() < spec.get("seed_chance", 0.03):
                empty_nbrs = [n for n in SLOT_NEIGHBORS[i]
                              if gs.flowers[n]["state"] == "E"]
                if empty_nbrs:
                    seeds_to_plant.append((random.choice(empty_nbrs), flower))
            if slot["age"] >= spec.get("bloom_life", 180):
                slot["state"] = "W"
                slot["age"]   = 0

        elif state == "W":
            # Wilting → return to empty ground
            slot["age"] += 2
            if slot["age"] >= 100:
                slot["state"]  = "E"
                slot["flower"] = "none"
                slot["age"]    = 0

    # Apply self-seeded arrivals (first seed wins per target slot)
    seeded: set[int] = set()
    for target, flower_key in seeds_to_plant:
        if target not in seeded and gs.flowers[target]["state"] == "E":
            gs.flowers[target]["state"]  = "B"
            gs.flowers[target]["flower"] = flower_key
            gs.flowers[target]["age"]    = 0
            seeded.add(target)


# --- Summary ---

def flower_summary(gs: GameState) -> dict:
    budding   = sum(1 for s in gs.flowers if s["state"] == "B")
    flowering = sum(1 for s in gs.flowers if s["state"] == "F")
    wilting   = sum(1 for s in gs.flowers if s["state"] == "W")
    empty     = sum(1 for s in gs.flowers if s["state"] == "E")
    return {
        "total":     FLOWER_SLOT_COUNT - empty,
        "budding":   budding,
        "flowering": flowering,
        "wilting":   wilting,
        "empty":     empty,
    }
