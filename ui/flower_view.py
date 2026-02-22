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


def run_flower_garden(stdscr: curses.window, gs: GameState) -> None:
    ensure_flower_garden(gs)

    cidx    = 0
    msg     = txt.FLOWER_ENTER
    running = True

    stdscr.nodelay(False)
    stdscr.keypad(True)

    while running:
        _draw_flower_garden(stdscr, gs, cidx, msg)
        msg = ""

        key = scr.get_key(stdscr)

        if key in ("UP", "DOWN", "LEFT", "RIGHT"):
            cidx = _navigate(cidx, key)
            continue

        elif key in ("p", "P"):
            slot = gs.flowers[cidx]
            if slot["state"] == "E":
                variety = _pick_flower(stdscr)
                if variety:
                    msg = action_plant_flower(gs, cidx, variety)
                    flower_tick(gs)
                else:
                    msg = "you leave it."
            else:
                msg = txt.FLOWER_PLANT_OCCUPIED

        elif key in ("q", "Q", "ESC"):
            running = False
            _flash_msg(stdscr, txt.FLOWER_LEAVE)


def _navigate(cidx: int, direction: str) -> int:
    """Return the index of the best neighbour in the given direction."""
    _, ro, co = FLOWER_SLOTS[cidx]          # unpack 3-tuple
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
        _, nr, nc  = FLOWER_SLOTS[nbr_idx]  # unpack 3-tuple
        score      = (nr - ro) * pr + (nc - co) * pc
        if score > best_score:
            best_score = score
            best_idx   = nbr_idx

    return best_idx


def _draw_flower_garden(stdscr: curses.window, gs: GameState,
                        cidx: int, msg: str) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    center_col = width // 2

    # --- Header ---
    header = f"[ flower garden — {gs.settlement_name} ]"
    scr.addstr(stdscr, 0, 2, header, scr.C_BRIGHT_WHITE, bold=True)
    if gs.flower_garden_unlocked_by:
        scr.addstr(stdscr, 0, 2 + len(header) + 2,
                   f"tended by {gs.flower_garden_unlocked_by}", scr.C_DIM)

    # --- Ambient text ---
    ambient_idx = (gs.action_count // 6) % len(txt.FLOWER_AMBIENT)
    scr.addstr(stdscr, 2, 2, txt.FLOWER_AMBIENT[ambient_idx], scr.C_DIM)

    # --- Diamond ---
    for i, (ring, ro, co) in enumerate(FLOWER_SLOTS):
        slot    = gs.flowers[i]
        state   = slot["state"]
        variety = slot["flower"]
        spec    = FLOWERS.get(variety, {})

        sr = CENTER_ROW + ro
        sc = center_col + co * 2

        is_cursor = (i == cidx)

        if state == "E":
            sym, pair, bold = ".", scr.C_DIM, False
        elif state == "B":
            sym  = "."
            pair = spec.get("color", scr.C_GREEN)
            bold = False
        elif state == "F":
            sym  = spec.get("bloom_sym", "*")
            pair = spec.get("color", scr.C_BRIGHT_YELLOW)
            bold = True
        elif state == "W":
            sym, pair, bold = "x", scr.C_DIM, False
        else:
            sym, pair, bold = "?", scr.C_DIM, False

        if is_cursor:
            scr.addstr(stdscr, sr, sc - 1, "[", scr.C_NORMAL, bold=True)
        scr.addstr(stdscr, sr, sc, sym, pair, bold=bold)
        if is_cursor:
            scr.addstr(stdscr, sr, sc + 1, "]", scr.C_NORMAL, bold=True)

    # --- Slot info (below diamond, row 11+) ---
    slot    = gs.flowers[cidx]
    state   = slot["state"]
    variety = slot["flower"]
    spec    = FLOWERS.get(variety, {})
    ring    = FLOWER_SLOTS[cidx][0]

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
