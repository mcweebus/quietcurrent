# ui/garden_view.py
# Curses rendering for the mycorrhizal network garden grid.

import curses
from engine.state import GameState, GARDEN_W, GARDEN_H, GARDEN_SIZE, plot_idx
from engine.garden import (
    garden_tick, action_inoculate, action_water,
    action_clear, action_enrich, action_add_compost, ensure_garden,
    EMPTY, HYPHA, NETWORK, MATURE, FRUITING, DECOMP, COMPETING,
)
from ui import screen as scr
from data import text as txt

# Plot symbols by state
PLOT_SYMBOLS = {
    "E": ".",
    "H": "o",
    "N": "+",
    "M": "#",
    "F": "*",
    "X": "%",
    "W": "w",
}


def run_garden(stdscr: curses.window, gs: GameState) -> None:
    ensure_garden(gs)

    cx, cy = 0, 0
    msg = txt.GARDEN_ENTER
    running = True

    stdscr.nodelay(False)
    stdscr.keypad(True)

    while running:
        _draw_garden(stdscr, gs, cx, cy, msg)
        msg = ""

        key = scr.get_key(stdscr)

        # Movement — drain held keys
        if key in ("UP", "DOWN", "LEFT", "RIGHT"):
            key = _drain_movement(stdscr, key)
            if key == "UP":    cy = max(0, cy - 1)
            elif key == "DOWN":  cy = min(GARDEN_H - 1, cy + 1)
            elif key == "LEFT":  cx = max(0, cx - 1)
            elif key == "RIGHT": cx = min(GARDEN_W - 1, cx + 1)
            continue

        elif key in ("i", "I"):
            msg = action_inoculate(gs, cx, cy)
            garden_tick(gs)

        elif key in ("w", "W"):
            msg = action_water(gs, cx, cy)
            garden_tick(gs)

        elif key in ("c", "C"):
            msg = action_clear(gs, cx, cy)
            garden_tick(gs)

        elif key in ("k", "K"):
            msg = action_enrich(gs, cx, cy)
            garden_tick(gs)

        elif key in ("+", "="):
            msg = action_add_compost(gs)

        elif key in ("q", "Q", "ESC"):
            running = False
            _flash_msg(stdscr, txt.GARDEN_LEAVE)


def _draw_garden(stdscr: curses.window, gs: GameState,
                 cx: int, cy: int, msg: str) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    # Header
    header = f"[ garden — {gs.settlement_name} ]"
    scr.addstr(stdscr, 0, 2, header, scr.C_BRIGHT_WHITE, bold=True)

    # Column numbers
    row = 2
    col_start = 6
    for x in range(GARDEN_W):
        label = str(x + 1).rjust(2)
        scr.addstr(stdscr, row, col_start + x * 2, label, scr.C_DIM)
    row += 1

    # Top border
    scr.addstr(stdscr, row, 4, "+" + "--" * GARDEN_W + "+", scr.C_DIM)
    row += 1

    # Grid rows
    for y in range(GARDEN_H):
        row_label = chr(ord("A") + y)
        scr.addstr(stdscr, row, 2, row_label, scr.C_DIM)
        scr.addstr(stdscr, row, 4, "|", scr.C_DIM)

        for x in range(GARDEN_W):
            p = gs.garden[plot_idx(x, y)]
            state = p["state"]
            is_cursor = (x == cx and y == cy)

            col = col_start + x * 2

            if is_cursor:
                scr.addstr(stdscr, row, col - 1, "[", scr.C_NORMAL, bold=True)

            sym  = PLOT_SYMBOLS.get(state, ".")
            pair = scr.PLOT_COLORS.get(state, scr.C_NORMAL)
            bold = state in ("M", "F")
            scr.addstr(stdscr, row, col, sym, pair, bold=bold)

            if is_cursor:
                scr.addstr(stdscr, row, col + 1, "]", scr.C_NORMAL, bold=True)

        scr.addstr(stdscr, row, col_start + GARDEN_W * 2, "|", scr.C_DIM)

        # Right panel: show selected plot info
        if y == cy:
            p = gs.garden[plot_idx(cx, cy)]
            state_name = txt.NETWORK_STATE_NAMES.get(p["state"], p["state"])
            soil_pair  = scr.SOIL_COLORS[min(5, max(1, p["soil"]))]
            moist_pair = scr.MOIST_COLORS[min(5, max(0, p["moisture"]))]

            # Count active neighbors
            conn = 0
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < GARDEN_W and 0 <= ny < GARDEN_H:
                    ns = gs.garden[plot_idx(nx, ny)]["state"]
                    if ns in (HYPHA, NETWORK, MATURE, FRUITING):
                        conn += 1

            info_col = col_start + GARDEN_W * 2 + 3
            scr.addstr(stdscr, row, info_col,
                       f"{state_name:<18}", scr.C_DIM)
            scr.addstr(stdscr, row, info_col + 19, "soil:", scr.C_DIM)
            scr.addstr(stdscr, row, info_col + 24, str(p["soil"]), soil_pair)
            scr.addstr(stdscr, row, info_col + 26, "moist:", scr.C_DIM)
            scr.addstr(stdscr, row, info_col + 32, str(p["moisture"]), moist_pair)
            scr.addstr(stdscr, row, info_col + 34, f"conn:{conn}", scr.C_DIM)

        row += 1

    # Bottom border
    scr.addstr(stdscr, row, 4, "+" + "--" * GARDEN_W + "+", scr.C_DIM)
    row += 2

    # Message
    if msg:
        scr.addstr(stdscr, row, 2, msg, scr.C_NORMAL)
        row += 1
    row += 1

    # Context hints
    p = gs.garden[plot_idx(cx, cy)]
    state = p["state"]
    hints = ["arrows:move"]
    if state == "E":                                   hints.append("i:inoculate")
    if state in ("H", "N", "M", "F"):                 hints.append("w:water")
    if state == "W":                                   hints.append("c:clear")
    if gs.has_compost_pile and state == "E":           hints.append("k:enrich")
    if gs.has_compost_pile:                            hints.append("+:compost")
    hints.append("q:leave")

    scr.addstr(stdscr, row, 2, "  ".join(hints), scr.C_DIM)
    row += 1

    # Resources footer
    res_line = f"spores:{gs.spores}  water:{gs.water}  mycelium:{gs.mycelium}"
    if gs.has_compost_pile:
        res_line += f"  compost:{gs.compost_level}/5"
    scr.addstr(stdscr, row, 2, res_line, scr.C_DIM)

    stdscr.refresh()


def _drain_movement(stdscr: curses.window, initial_key: str) -> str:
    """Consume queued arrow keys, return last one."""
    last = initial_key
    stdscr.nodelay(True)
    while True:
        try:
            k = stdscr.get_wch()
        except curses.error:
            break
        if isinstance(k, int):
            mapping = {
                curses.KEY_UP: "UP", curses.KEY_DOWN: "DOWN",
                curses.KEY_LEFT: "LEFT", curses.KEY_RIGHT: "RIGHT",
            }
            mapped = mapping.get(k)
            if mapped:
                last = mapped
            else:
                break
        else:
            break
    stdscr.nodelay(False)
    return last


def _flash_msg(stdscr: curses.window, msg: str) -> None:
    stdscr.erase()
    scr.addstr(stdscr, 3, 2, msg, scr.C_DIM)
    stdscr.refresh()
    curses.napms(800)
