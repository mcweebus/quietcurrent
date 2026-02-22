# ui/garden_view.py
# Curses rendering for the garden grid.

import curses
from engine.state import GameState, GARDEN_W, GARDEN_H, GARDEN_SIZE, plot_idx
from engine.garden import (
    PollinatorSystem, garden_tick, action_dig, action_plant,
    action_water, action_harvest, action_clear_weeds,
    action_apply_compost, action_add_compost, ensure_garden,
)
from ui import screen as scr
from data import text as txt

# Plot symbols by state
PLOT_SYMBOLS = {
    "E": ".",
    "D": "_",
    "P": "o",
    "G": "%",
    "R": "*",
    "W": "w",
    "X": "x",
}

CROP_KEYS = list(txt.CROPS.keys())


def run_garden(stdscr: curses.window, gs: GameState) -> None:
    ensure_garden(gs)
    pollinators = PollinatorSystem()

    cx, cy = 0, 0
    msg = txt.GARDEN_ENTER
    running = True

    stdscr.nodelay(False)
    stdscr.keypad(True)

    while running:
        pollinators.tick(gs)
        _draw_garden(stdscr, gs, pollinators, cx, cy, msg)
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

        elif key in ("d", "D"):
            msg = action_dig(gs, cx, cy)
            garden_tick(gs)

        elif key in ("p", "P"):
            crop = _pick_crop(stdscr, gs)
            if crop:
                msg = action_plant(gs, cx, cy, crop)
                garden_tick(gs)
            else:
                msg = "nothing planted."

        elif key in ("w", "W"):
            msg = action_water(gs, cx, cy)
            garden_tick(gs)

        elif key in ("h", "H"):
            bonus = pollinators.nearby(cx, cy)
            msg = action_harvest(gs, cx, cy, pollinator_bonus=bonus)
            garden_tick(gs)

        elif key in ("c", "C"):
            msg = action_clear_weeds(gs, cx, cy)
            garden_tick(gs)

        elif key in ("k", "K"):
            msg = action_apply_compost(gs, cx, cy)
            garden_tick(gs)

        elif key in ("+", "="):
            msg = action_add_compost(gs)

        elif key in ("q", "Q", "ESC"):
            running = False
            _flash_msg(stdscr, txt.GARDEN_LEAVE)


def _draw_garden(stdscr: curses.window, gs: GameState,
                 pollinators: PollinatorSystem,
                 cx: int, cy: int, msg: str) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    # Header
    header = f"[ garden — {gs.settlement_name} ]"
    scr.addstr(stdscr, 0, 2, header, scr.C_BRIGHT_WHITE, bold=True)

    poll_active = len(pollinators.positions) > 0
    if poll_active:
        scr.addstr(stdscr, 0, 2 + len(header) + 3,
                   txt.POLLINATOR_PRESENT, scr.C_BRIGHT_YELLOW, bold=True)

    # Column numbers
    row = 2
    scr.addstr(stdscr, row, 5, "", scr.C_DIM)
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

            has_poll = pollinators.at(x, y)
            is_cursor = (x == cx and y == cy)

            col = col_start + x * 2

            if is_cursor:
                scr.addstr(stdscr, row, col - 1, "[", scr.C_NORMAL, bold=True)

            if has_poll:
                scr.addstr(stdscr, row, col, "✦",
                           scr.C_BRIGHT_YELLOW, bold=True)
            else:
                sym   = PLOT_SYMBOLS.get(state, ".")
                pair  = scr.PLOT_COLORS.get(state, scr.C_NORMAL)
                bold  = state in ("R",)
                scr.addstr(stdscr, row, col, sym, pair, bold=bold)

            if is_cursor:
                scr.addstr(stdscr, row, col + 1, "]", scr.C_NORMAL, bold=True)

        scr.addstr(stdscr, row, col_start + GARDEN_W * 2, "|", scr.C_DIM)

        # Show selected row info on the right
        if y == cy:
            p = gs.garden[plot_idx(cx, cy)]
            soil_pair  = scr.SOIL_COLORS[min(5, max(1, p["soil"]))]
            moist_pair = scr.MOIST_COLORS[min(5, max(0, p["moisture"]))]
            info_col   = col_start + GARDEN_W * 2 + 3
            scr.addstr(stdscr, row, info_col, "soil:", scr.C_DIM)
            scr.addstr(stdscr, row, info_col + 5, str(p["soil"]), soil_pair)
            scr.addstr(stdscr, row, info_col + 7, "moist:", scr.C_DIM)
            scr.addstr(stdscr, row, info_col + 13, str(p["moisture"]), moist_pair)
            crop = p["crop"] if p["crop"] != "none" else "-"
            scr.addstr(stdscr, row, info_col + 16, f"crop:{crop:<10}", scr.C_DIM)
            scr.addstr(stdscr, row, info_col + 32, f"grow:{p['growth']}%", scr.C_DIM)

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
    if state == "E":                              hints.append("d:dig")
    if state == "D" and gs.seeds > 0:            hints.append("p:plant")
    if state in ("D", "P", "G"):                 hints.append("w:water")
    if state == "R":                              hints.append("h:harvest")
    if state == "W":                              hints.append("c:clear weeds")
    if gs.has_compost_pile and state == "D":      hints.append("k:compost")
    hints.append("q:leave")

    scr.addstr(stdscr, row, 2, "  ".join(hints), scr.C_DIM)
    row += 1

    # Resources
    res_line = f"water:{gs.water}  seeds:{gs.seeds}"
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


def _pick_crop(stdscr: curses.window, gs: GameState) -> str | None:
    crops = list(txt.CROPS.items())
    selected = 0
    while True:
        stdscr.erase()
        scr.addstr(stdscr, 1, 2, "what will you plant?",
                   scr.C_BRIGHT_WHITE, bold=True)
        for i, (key, crop) in enumerate(crops):
            prefix = "> " if i == selected else "  "
            scr.addstr(stdscr, 3 + i, 2,
                       f"{prefix}{crop['label']:<12} {crop['desc']}",
                       scr.C_NORMAL, bold=(i == selected))
        scr.addstr(stdscr, 3 + len(crops) + 1, 2,
                   "↑↓ select   enter: plant   q: cancel", scr.C_DIM)
        stdscr.refresh()

        key = scr.get_key(stdscr)
        if key == "UP":    selected = max(0, selected - 1)
        elif key == "DOWN":  selected = min(len(crops) - 1, selected + 1)
        elif key in ("\n", "\r", " "):
            return crops[selected][0]
        elif key in ("q", "Q", "ESC"):
            return None


def _flash_msg(stdscr: curses.window, msg: str) -> None:
    stdscr.erase()
    scr.addstr(stdscr, 3, 2, msg, scr.C_DIM)
    stdscr.refresh()
    curses.napms(800)
