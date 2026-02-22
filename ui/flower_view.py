# ui/flower_view.py
# Curses rendering for the flower garden (radial diamond layout).

import curses
from engine.state import GameState
from engine.flowers import (
    FLOWERS, FLOWER_SLOTS, SLOT_NEIGHBORS,
    ensure_flower_garden, action_plant_flower, flower_tick,
)
from ui import screen as scr
from data import text as txt

# FLOWER_SLOTS entries are (ring, row_off, col_off) 3-tuples.
# Screen formula: screen_row = center_row + ro
#                 screen_col = center_col + co * 2
# FLOWERS[key]["color"] is already an integer pair ID (same values as scr.C_*).

CENTER_ROW = 8   # row of diamond centre; diamond spans rows 6–10


# ── Animation ─────────────────────────────────────────────────

# Sway patterns: list of offsets (-1 left, 0 centre, +1 right) per frame step.
# Each slot is phase-shifted by slot_idx * 7 so they don't all move together.
_SWAY_PATTERNS = {
    "sunny":  [0,0,0,0,0,0,0,0,0,0, 1,0,0,0,0,0,0,0,0,0,
               0,0,0,0,-1,0,0,0,0,0],       # rare, brief lean — mostly still
    "cloudy": [0,0,0, 1,0,0,0,0,-1,0,
               0,0, 1,0,0,0,-1,0,0,0],      # gentle periodic drift
    "windy":  [0, 1, 1, 0,-1,-1],           # fast, pronounced, asymmetric
    "rainy":  [-1,-1,-1,-1, 0,-1,-1,-1,-1,-1, 0,-1],  # heavy hang, mostly left
}


def _sway_offset(frame: int, slot_idx: int, weather: str) -> int:
    pattern = _SWAY_PATTERNS.get(weather, _SWAY_PATTERNS["cloudy"])
    phase   = (frame + slot_idx * 7) % len(pattern)
    return pattern[phase]


def _bud_pair(slot_idx: int, frame: int, spec_color: int) -> int:
    """Pulse budding flowers between their colour and dim."""
    phase = (frame + slot_idx * 5) % 20
    return spec_color if phase < 14 else scr.C_DIM


# ── Main entry ─────────────────────────────────────────────────

def run_flower_garden(stdscr: curses.window, gs: GameState) -> None:
    ensure_flower_garden(gs)

    cidx    = 0
    msg     = txt.FLOWER_ENTER
    running = True
    frame   = 0

    stdscr.nodelay(True)
    stdscr.keypad(True)

    while running:
        _draw_flower_garden(stdscr, gs, cidx, msg, frame)

        key = scr.get_key(stdscr)

        if not key:
            curses.napms(120)   # ~8 fps
            frame += 1
            continue

        msg = ""   # clear message on any keypress

        if key in ("UP", "DOWN", "LEFT", "RIGHT"):
            cidx = _navigate(cidx, key)

        elif key in ("p", "P"):
            slot = gs.flowers[cidx]
            if slot["state"] == "E":
                stdscr.nodelay(False)
                variety = _pick_flower(stdscr)
                stdscr.nodelay(True)
                if variety:
                    msg = action_plant_flower(gs, cidx, variety)
                    flower_tick(gs)
                else:
                    msg = "you leave it."
            else:
                msg = txt.FLOWER_PLANT_OCCUPIED

        elif key in ("q", "Q", "ESC"):
            running = False
            stdscr.nodelay(False)
            _flash_msg(stdscr, txt.FLOWER_LEAVE)

    stdscr.nodelay(False)


# ── Navigation ────────────────────────────────────────────────

def _navigate(cidx: int, direction: str) -> int:
    """Return the index of the best neighbour in the given direction."""
    _, ro, co = FLOWER_SLOTS[cidx]
    pref = {
        "UP":    (-1,  0),
        "DOWN":  ( 1,  0),
        "LEFT":  ( 0, -1),
        "RIGHT": ( 0,  1),
    }
    pr, pc = pref[direction]
    best_idx   = cidx
    best_score = 0

    for nbr_idx in SLOT_NEIGHBORS[cidx]:
        _, nr, nc  = FLOWER_SLOTS[nbr_idx]
        score      = (nr - ro) * pr + (nc - co) * pc
        if score > best_score:
            best_score = score
            best_idx   = nbr_idx

    return best_idx


# ── Drawing ───────────────────────────────────────────────────

def _draw_flower_garden(stdscr: curses.window, gs: GameState,
                        cidx: int, msg: str, frame: int) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    center_col = width // 2

    # --- Header ---
    header = f"[ flower garden — {gs.settlement_name} ]"
    scr.addstr(stdscr, 0, 2, header, scr.C_BRIGHT_WHITE, bold=True)
    if gs.flower_garden_unlocked_by:
        scr.addstr(stdscr, 0, 2 + len(header) + 2,
                   f"tended by {gs.flower_garden_unlocked_by}", scr.C_DIM)

    # --- Ambient text (cycles every ~7 s at 8 fps) ---
    ambient_idx = (frame // 60) % len(txt.FLOWER_AMBIENT)
    scr.addstr(stdscr, 2, 2, txt.FLOWER_AMBIENT[ambient_idx], scr.C_DIM)

    # --- Diamond ---
    for i, (ring, ro, co) in enumerate(FLOWER_SLOTS):
        slot      = gs.flowers[i]
        state     = slot["state"]
        variety   = slot["flower"]
        spec      = FLOWERS.get(variety, {})
        is_cursor = (i == cidx)

        sr = CENTER_ROW + ro
        sc = center_col + co * 2

        sway = _sway_offset(frame, i, gs.weather)

        if state == "E":
            if is_cursor:
                scr.addstr(stdscr, sr, sc - 1, "[", scr.C_NORMAL, bold=True)
                scr.addstr(stdscr, sr, sc,     ".", scr.C_DIM)
                scr.addstr(stdscr, sr, sc + 1, "]", scr.C_NORMAL, bold=True)
            else:
                scr.addstr(stdscr, sr, sc, ".", scr.C_DIM)
            continue

        # Resolve bloom appearance per state
        if state == "B":
            bloom_sym  = "."
            bloom_pair = _bud_pair(i, frame, spec.get("color", scr.C_GREEN))
            bloom_bold = False
        elif state == "F":
            bloom_sym  = spec.get("bloom_sym", "*")
            bloom_pair = spec.get("color", scr.C_BRIGHT_YELLOW)
            bloom_bold = True
        elif state == "W":
            sway       = -1 if i % 2 == 0 else 1   # fixed droop direction per slot
            bloom_sym  = "x" if (frame + i * 3) % 12 < 8 else "."
            bloom_pair = scr.C_DIM
            bloom_bold = False
        else:
            bloom_sym, bloom_pair, bloom_bold = "?", scr.C_DIM, False

        bloom_col = sc + sway
        stem_char = "/" if sway > 0 else ("\\" if sway < 0 else "")

        if is_cursor:
            # Cursor brackets wrap the whole bloom+stem unit
            if sway == 0:
                scr.addstr(stdscr, sr, sc - 1,        "[",        scr.C_NORMAL, bold=True)
                scr.addstr(stdscr, sr, sc,             bloom_sym,  bloom_pair,   bold=bloom_bold)
                scr.addstr(stdscr, sr, sc + 1,         "]",        scr.C_NORMAL, bold=True)
            elif sway > 0:
                # stem at sc, bloom at sc+1  →  [ / bloom ]
                scr.addstr(stdscr, sr, sc - 1,         "[",        scr.C_NORMAL, bold=True)
                scr.addstr(stdscr, sr, sc,              stem_char,  scr.C_DIM)
                scr.addstr(stdscr, sr, bloom_col,       bloom_sym,  bloom_pair,   bold=bloom_bold)
                scr.addstr(stdscr, sr, bloom_col + 1,   "]",        scr.C_NORMAL, bold=True)
            else:
                # bloom at sc-1, stem at sc  →  [ bloom \ ]
                scr.addstr(stdscr, sr, bloom_col - 1,  "[",        scr.C_NORMAL, bold=True)
                scr.addstr(stdscr, sr, bloom_col,       bloom_sym,  bloom_pair,   bold=bloom_bold)
                scr.addstr(stdscr, sr, sc,              stem_char,  scr.C_DIM)
                scr.addstr(stdscr, sr, sc + 1,          "]",        scr.C_NORMAL, bold=True)
        else:
            if stem_char:
                scr.addstr(stdscr, sr, sc, stem_char, scr.C_DIM)
            scr.addstr(stdscr, sr, bloom_col, bloom_sym, bloom_pair, bold=bloom_bold)

    # --- Slot info (below diamond) ---
    slot    = gs.flowers[cidx]
    state   = slot["state"]
    variety = slot["flower"]
    spec    = FLOWERS.get(variety, {})

    info_row = CENTER_ROW + 3

    state_labels = {
        "E": "empty",
        "B": f"budding  {int(slot['age'])}%",
        "F": f"flowering  {slot['age']} ticks",
        "W": f"wilting  {int(slot['age'])}%",
    }
    state_str = state_labels.get(state, state)

    if variety != "none":
        pair = spec.get("color", scr.C_NORMAL)
        scr.addstr(stdscr, info_row, 2,
                   f"{spec.get('label', variety)}  —  {state_str}",
                   pair, bold=(state == "F"))
        scr.addstr(stdscr, info_row + 1, 2, spec.get("desc", ""), scr.C_DIM)
    else:
        scr.addstr(stdscr, info_row, 2, state_str, scr.C_DIM)

    # --- Message ---
    msg_row = CENTER_ROW + 6
    if msg:
        scr.addstr(stdscr, msg_row, 2, msg, scr.C_NORMAL)

    # --- Hints ---
    hints = ["arrows:move"]
    if slot["state"] == "E":
        hints.append("p:plant")
    hints.append("q:leave")
    scr.addstr(stdscr, msg_row + 2, 2, "  ".join(hints), scr.C_DIM)

    stdscr.refresh()


# ── Planting ──────────────────────────────────────────────────

def _pick_flower(stdscr: curses.window) -> str | None:
    flowers  = list(FLOWERS.items())
    selected = 0

    while True:
        stdscr.erase()
        scr.addstr(stdscr, 1, 2, "what will you plant?",
                   scr.C_BRIGHT_WHITE, bold=True)

        for i, (key, spec) in enumerate(flowers):
            prefix = "> " if i == selected else "  "
            pair   = spec.get("color", scr.C_NORMAL) if i == selected else scr.C_NORMAL
            line   = (f"{prefix}{spec['bloom_sym']} "
                      f"{spec['label']:<12} {spec['desc']}")
            scr.addstr(stdscr, 3 + i, 2, line, pair, bold=(i == selected))

        scr.addstr(stdscr, 3 + len(flowers) + 1, 2,
                   "↑↓ select   enter: plant   q: cancel", scr.C_DIM)
        stdscr.refresh()

        key = scr.get_key(stdscr)
        if key == "UP":
            selected = max(0, selected - 1)
        elif key == "DOWN":
            selected = min(len(flowers) - 1, selected + 1)
        elif key in ("\n", "\r", " "):
            return flowers[selected][0]
        elif key in ("q", "Q", "ESC"):
            return None


def _flash_msg(stdscr: curses.window, msg: str) -> None:
    stdscr.erase()
    scr.addstr(stdscr, 3, 2, msg, scr.C_DIM)
    stdscr.refresh()
    curses.napms(800)
