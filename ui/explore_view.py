# ui/explore_view.py
# Curses rendering for the exploration map.

import curses
import random
from engine.state import GameState
from engine import world
from ui import screen as scr
from data import text as txt

MAP_W = 36
MAP_H = 14

TERRAIN_COLORS = {
    ".": scr.C_DIM,
    "#": scr.C_NORMAL,
    "~": scr.C_CYAN,
    "^": scr.C_YELLOW,
    "*": scr.C_BRIGHT_YELLOW,
    "H": scr.C_BRIGHT_GREEN,
    "@": scr.C_BRIGHT_WHITE,
}


def _gen_map() -> list[list[str]]:
    grid = []
    for y in range(MAP_H):
        row = []
        for x in range(MAP_W):
            r = random.randint(0, 99)
            if r < 65:   row.append(".")
            elif r < 78: row.append("#")
            elif r < 84: row.append("~")
            elif r < 91: row.append("^")
            else:        row.append("*")
        grid.append(row)
    grid[0][0] = "H"
    return grid


def _load_grid(flat: list) -> list[list[str]]:
    return [[flat[y * MAP_W + x] for x in range(MAP_W)] for y in range(MAP_H)]


def _save_grid(gs: GameState, grid: list[list[str]]) -> None:
    gs.explore_map = [grid[y][x] for y in range(MAP_H) for x in range(MAP_W)]


def run_explore(stdscr: curses.window, gs: GameState,
                bonus_hp: int = 0) -> str | None:
    if gs.explore_map and len(gs.explore_map) == MAP_W * MAP_H:
        grid = _load_grid(gs.explore_map)
    else:
        grid = _gen_map()

    visited: set[tuple[int, int]] = {(v[0], v[1]) for v in gs.explore_visited}
    visited.add((0, 0))

    px, py = 0, 0
    hp = 5 + bonus_hp
    pack = {"scrap": 0, "water": 0, "spores": 0}
    msg = random.choice(txt.EXPLORE_DEPART).format(name=gs.settlement_name)
    running = True
    result_msg = None

    stdscr.nodelay(False)
    stdscr.keypad(True)

    # Brief departure text
    stdscr.erase()
    scr.addstr(stdscr, 3, 2, msg, scr.C_DIM)
    stdscr.refresh()
    curses.napms(1500)

    while running:
        _draw_explore(stdscr, gs, grid, px, py, hp, pack, msg, visited)
        msg = ""

        key = scr.get_key(stdscr)

        dx, dy = 0, 0
        if key == "UP":    dy = -1
        elif key == "DOWN":  dy = 1
        elif key == "LEFT":  dx = -1
        elif key == "RIGHT": dx = 1
        elif key in ("h", "H", "q", "Q"):
            running = False
            result_msg = _return_home(gs, gs.settlement_name, pack)
            continue

        if dx or dy:
            nx, ny = px + dx, py + dy
            nx = max(0, min(MAP_W - 1, nx))
            ny = max(0, min(MAP_H - 1, ny))

            cell = grid[ny][nx]
            if cell == "#":
                msg = "the way is blocked."
            else:
                px, py = nx, ny
                visited.add((px, py))
                msg, hp = _handle_cell(grid, px, py, hp, pack)

        if hp <= 0:
            running = False
            frag = world.explore_die(gs)
            stdscr.erase()
            for i, line in enumerate(txt.EXPLORE_DEATH):
                text = line.format(name=gs.settlement_name)
                scr.addstr(stdscr, 3 + i * 2, 2, text, scr.C_DIM)
            if frag:
                scr.addstr(stdscr, 3 + len(txt.EXPLORE_DEATH) * 2 + 1,
                            2, frag, scr.C_MAGENTA)
            stdscr.refresh()
            curses.napms(3000)
            result_msg = None

    # Persist map state and visited knowledge regardless of exit path
    _save_grid(gs, grid)
    gs.explore_visited = [[x, y] for x, y in visited]

    return result_msg


def _handle_cell(grid, px, py, hp, pack) -> tuple[str, int]:
    cell = grid[py][px]
    msg = ""

    if cell == "~":
        hp -= 1
        msg = "the ground is saturated. difficult going."
    elif cell == "^":
        msg = random.choice(txt.EXPLORE_HIGH_GROUND)
    elif cell == "*":
        msg, pack = _loot(pack)
        grid[py][px] = "."
    elif cell == ".":
        if random.random() < 0.12:
            msg, hp = _encounter(hp)

    return msg, hp


def _loot(pack: dict) -> tuple[str, dict]:
    r = random.randint(0, 99)
    if r < 50:
        amt = random.randint(1, 3)
        pack["scrap"] += amt
        return f"{random.choice(txt.EXPLORE_LOOT_SCRAP)} (+{amt} scrap)", pack
    elif r < 75:
        amt = random.randint(1, 2)
        pack["water"] += amt
        return f"{random.choice(txt.EXPLORE_LOOT_WATER)} (+{amt} water)", pack
    else:
        pack["spores"] += 1
        return f"{random.choice(txt.EXPLORE_LOOT_SPORES)} (+1 spores)", pack


def _encounter(hp: int) -> tuple[str, int]:
    if random.random() < 0.72:
        return random.choice(txt.EXPLORE_ENCOUNTERS_SAFE), hp
    dmg = random.randint(1, 2)
    hp -= dmg
    return f"{random.choice(txt.EXPLORE_ENCOUNTERS_HARM)} (-{dmg} hp)", hp


def _return_home(gs: GameState, name: str, pack: dict) -> str:
    gs.scrap  += pack["scrap"]
    gs.water  += pack["water"]
    gs.spores += pack["spores"]

    msg = txt.EXPLORE_RETURN.format(name=name)
    parts = []
    if pack["scrap"]:  parts.append(f"+{pack['scrap']} scrap")
    if pack["water"]:  parts.append(f"+{pack['water']} water")
    if pack["spores"]: parts.append(f"+{pack['spores']} spores")
    if parts:
        msg += " — " + ", ".join(parts)
    else:
        msg += f", {txt.EXPLORE_RETURN_EMPTY}"
    return msg + "."


def _draw_explore(stdscr, gs, grid, px, py, hp, pack, msg, visited) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    # Stats line
    pack_str = (f"scrap:{pack['scrap']}  water:{pack['water']}  "
                f"spores:{pack['spores']}")
    scr.addstr(stdscr, 0, 2, f"hp:{hp}   {pack_str}", scr.C_DIM)

    # Map border
    border_top = 2
    scr.addstr(stdscr, border_top, 2, "+" + "-" * MAP_W + "+", scr.C_DIM)

    for y in range(MAP_H):
        scr.addstr(stdscr, border_top + 1 + y, 2, "|", scr.C_DIM)
        for x in range(MAP_W):
            if x == px and y == py:
                scr.addstr(stdscr, border_top + 1 + y, 3 + x,
                           "@", scr.C_BRIGHT_WHITE, bold=True)
            elif (x, y) in visited:
                cell = grid[y][x]
                pair = TERRAIN_COLORS.get(cell, scr.C_DIM)
                scr.addstr(stdscr, border_top + 1 + y, 3 + x, cell, pair)
            else:
                scr.addstr(stdscr, border_top + 1 + y, 3 + x, "?", scr.C_DIM)
        scr.addstr(stdscr, border_top + 1 + y, 3 + MAP_W, "|", scr.C_DIM)

    bottom = border_top + MAP_H + 1
    scr.addstr(stdscr, bottom, 2, "+" + "-" * MAP_W + "+", scr.C_DIM)

    # Message
    if msg:
        scr.addstr(stdscr, bottom + 2, 2, msg, scr.C_NORMAL)

    # Controls
    scr.addstr(stdscr, bottom + 3, 2,
               "arrows:move   h:return home", scr.C_DIM)

    stdscr.refresh()
