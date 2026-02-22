# main.py
# Entry point. Curses wrapper → game loop.

import curses
import sys
import random
import time

from engine.state import GameState, save_game, load_game, days_since_last_seen
from engine import panel as pan
from engine import garden as gdn
from engine import residents as res
from engine import world
from ui import screen as scr
from data import text as txt


# ── Main game loop ────────────────────────────────────────────

def game_loop(stdscr: curses.window, gs: GameState) -> None:
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)
    scr.init_colors()

    flashes: list[str] = []
    current_wanderer: dict | None = None

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.erase()

        # --- Draw status screen ---
        row = 0
        scr.addstr(stdscr, row, 2, gs.settlement_name,
                   scr.C_BRIGHT_WHITE, bold=True)
        row += 1

        # Weather + efficiency
        weather_sym = txt.WEATHER_SYMBOLS.get(gs.weather, "?")
        weather_line = f"{weather_sym} {gs.weather}"
        if pan.panel_connected(gs):
            eff = gs.panel_efficiency
            eff_pair = scr.C_BRIGHT_GREEN
            if eff < 75: eff_pair = scr.C_BRIGHT_YELLOW
            if eff < 50: eff_pair = scr.C_YELLOW
            if eff < 25: eff_pair = scr.C_RED
            scr.addstr(stdscr, row, 2, weather_line, scr.C_NORMAL)
            scr.addstr(stdscr, row, 2 + len(weather_line) + 3,
                       f"panel: {eff}%", eff_pair)
            if pan.needs_maintenance(gs):
                scr.addstr(stdscr, row,
                           2 + len(weather_line) + 3 + len(f"panel: {eff}%") + 2,
                           "[needs attention]", scr.C_BRIGHT_YELLOW, bold=True)
        else:
            scr.addstr(stdscr, row, 2, weather_line, scr.C_DIM)
        row += 2

        # Panel description
        scr.addstr(stdscr, row, 2, pan.panel_description(gs), scr.C_DIM)
        row += 2

        # Structures
        structures = []
        if gs.has_junction_box:   structures.append("junction box")
        if gs.has_rain_catcher:   structures.append("rain catcher")
        if gs.has_garden_bed:     structures.append("garden bed")
        if gs.has_signal_beacon:  structures.append("signal beacon")
        if gs.has_compost_pile:   structures.append(f"compost pile [{gs.compost_level}/5]")
        if structures:
            scr.addstr(stdscr, row, 2, "  ".join(structures), scr.C_DIM)
            row += 1

        # Residents
        if gs.residents:
            row += 1
            for r in gs.residents:
                mood_pair = scr.MOOD_COLORS.get(r["mood"], scr.C_NORMAL)
                mood_label = txt.MOOD_LABELS.get(r["mood"], "")
                scr.addstr(stdscr, row, 2, f"{r['name']:<10}", scr.C_NORMAL)
                scr.addstr(stdscr, row, 12, mood_label, mood_pair)
                row += 1

        # Resources
        row += 1
        resources = [
            ("power", gs.power,  scr.C_BRIGHT_YELLOW),
            ("water", gs.water,  scr.C_CYAN),
            ("seeds", gs.seeds,  scr.C_BRIGHT_GREEN),
            ("scrap", gs.scrap,  scr.C_YELLOW),
        ]
        col = 2
        for label, val, pair in resources:
            scr.addstr(stdscr, row,   col, label, pair)
            scr.addstr(stdscr, row+1, col, str(val), scr.C_NORMAL)
            col += 10
        row += 3

        # Flash messages
        for flash in flashes:
            scr.addstr(stdscr, row, 2, flash, scr.C_DIM)
            row += 1
        if flashes:
            row += 1
        flashes.clear()

        # Divider
        scr.draw_hline(stdscr, row, 2, "─", min(width - 4, 44), scr.C_DIM)
        row += 1

        # Menu
        menu_start = row
        menu_items: list[tuple[str, str]] = []

        menu_items.append(("1", _tend_label(gs)))
        if gs.panel_state != "neglected" or gs.tend_count > 0:
            menu_items.append(("2", "go outside"))
        if _can_build(gs):
            menu_items.append(("3", "build"))
        if gs.has_garden_bed:
            menu_items.append(("g", "tend the garden"))
        if current_wanderer:
            menu_items.append(("4", f"speak with {current_wanderer['name']}"))
        menu_items.append(("q", "leave for now"))

        for key, label in menu_items:
            scr.addstr(stdscr, row, 2, f"{key})", scr.C_DIM)
            scr.addstr(stdscr, row, 5, label, scr.C_NORMAL)
            row += 1

        stdscr.refresh()

        # --- Input ---
        key = scr.get_key(stdscr)
        if not key:
            continue

        if key == "q":
            save_game(gs)
            break

        elif key == "1":
            result, ancestral = do_tend(gs)
            tick = world.tick_all(gs)
            _collect_flashes(flashes, result, ancestral,
                             tick.panel_flash, tick.resident_flash,
                             tick.passive_flash)
            save_game(gs)

        elif key == "2":
            if gs.panel_state != "neglected" or gs.tend_count > 0:
                from ui.explore_view import run_explore
                result = run_explore(stdscr, gs)
                if result:
                    flashes.append(result)
                save_game(gs)

        elif key == "3":
            if _can_build(gs):
                result = run_build_menu(stdscr, gs)
                if result:
                    flashes.append(result)
                tick = world.tick_all(gs)
                _collect_flashes(flashes, tick.panel_flash,
                                 tick.resident_flash, tick.passive_flash)
                save_game(gs)

        elif key == "g" and gs.has_garden_bed:
            from ui.garden_view import run_garden
            run_garden(stdscr, gs)
            save_game(gs)

        elif key == "4" and current_wanderer:
            result = run_wanderer_menu(stdscr, gs, current_wanderer)
            stay_result = world.resolve_stay(gs, current_wanderer)
            if result:   flashes.append(result)
            if stay_result: flashes.append(stay_result)
            current_wanderer = None
            tick = world.tick_all(gs)
            _collect_flashes(flashes, tick.panel_flash,
                             tick.resident_flash, tick.passive_flash)
            save_game(gs)

        # Check wanderer arrival each action
        if not current_wanderer and key in ("1", "2", "3", "g"):
            current_wanderer = world.check_wanderer_arrival(gs)
            if current_wanderer:
                flashes.append(
                    f"{current_wanderer['name']} is here. "
                    f"{current_wanderer['desc']}"
                )


# ── Tend ──────────────────────────────────────────────────────

def _tend_label(gs: GameState) -> str:
    if gs.panel_state == "neglected":  return "clean the panel"
    if gs.panel_state == "cleaned":    return "connect the panel"
    if pan.needs_maintenance(gs):      return "tend the panel  [needs attention]"
    return "tend the panel"


def do_tend(gs: GameState) -> tuple[str, str | None]:
    gs.tend_count += 1
    ancestral = world.check_ancestral_milestone(gs)

    if gs.panel_state == "neglected":
        if gs.tend_count >= 3:
            gs.panel_state = "cleaned"
            return txt.PANEL_CLEAN_TRANSITION, ancestral
        return random.choice(txt.PANEL_NEGLECTED_TEND), ancestral

    if gs.panel_state == "cleaned":
        if gs.scrap >= 2:
            gs.scrap -= 2
            gs.panel_state = "connected"
            gs.power += 1
            pan.recalc_efficiency(gs)
            return txt.PANEL_CONNECT_TRANSITION, ancestral
        return txt.PANEL_CONNECT_NEED_SCRAP, ancestral

    # Connected — maintenance submenu
    if pan.needs_maintenance(gs):
        result = run_maintenance_menu(None, gs)  # inline for now
        return result, ancestral

    gs.power += 1
    return random.choice(txt.PANEL_MAINTAIN_OK), ancestral


def run_maintenance_menu(stdscr, gs: GameState) -> str:
    """Inline maintenance — simplified for main loop context."""
    conditions = pan.active_conditions(gs)
    if not conditions:
        return random.choice(txt.PANEL_MAINTAIN_OK)
    # Auto-apply first fixable condition for now
    # Full curses menu rendered in a dedicated draw pass
    cond = conditions[0]
    return pan.do_maintain(gs, cond)


# ── Build menu ────────────────────────────────────────────────

def _can_build(gs: GameState) -> bool:
    return gs.panel_state not in ("neglected", "cleaned")


def run_build_menu(stdscr: curses.window, gs: GameState) -> str | None:
    buildings = txt.BUILDINGS
    affordable = []
    for b in buildings:
        flag = f"has_{b['key']}"
        if getattr(gs, flag, False):
            continue
        cost = b["cost"]
        can_afford = all(getattr(gs, r, 0) >= amt for r, amt in cost.items())
        affordable.append((b, can_afford))

    if not affordable:
        return "nothing left to build."

    selected = 0
    while True:
        stdscr.erase()
        scr.addstr(stdscr, 1, 2, "[ build ]", scr.C_BRIGHT_WHITE, bold=True)
        row = 3
        for i, (b, can_afford) in enumerate(affordable):
            prefix = "> " if i == selected else "  "
            cost_str = "  ".join(f"{r}: {amt}" for r, amt in b["cost"].items())
            pair = scr.C_NORMAL if can_afford else scr.C_DIM
            scr.addstr(stdscr, row, 2, f"{prefix}{b['label']:<20} {cost_str}",
                       pair, bold=(i == selected))
            row += 1

        row += 1
        scr.addstr(stdscr, row, 2,
                   "↑↓ select   enter: build   q: back", scr.C_DIM)
        stdscr.refresh()

        key = scr.get_key(stdscr)
        if key == "UP":
            selected = max(0, selected - 1)
        elif key == "DOWN":
            selected = min(len(affordable) - 1, selected + 1)
        elif key in ("\n", "\r", " "):
            b, can_afford = affordable[selected]
            if not can_afford:
                continue
            for r, amt in b["cost"].items():
                setattr(gs, r, getattr(gs, r) - amt)
            setattr(gs, f"has_{b['key']}", True)
            return random.choice(b["built"])
        elif key in ("q", "Q", "ESC"):
            return None


# ── Wanderer menu ─────────────────────────────────────────────

def run_wanderer_menu(stdscr: curses.window, gs: GameState,
                      wanderer: dict) -> str | None:
    while True:
        stdscr.erase()
        scr.addstr(stdscr, 1, 2, wanderer["name"],
                   scr.C_BRIGHT_WHITE, bold=True)
        scr.addstr(stdscr, 2, 2, wanderer["desc"], scr.C_DIM)
        scr.addstr(stdscr, 4, 2,
                   f"offers: {wanderer['give_amt']} {wanderer['give']}",
                   scr.C_GREEN)
        scr.addstr(stdscr, 5, 2,
                   f"wants:  {wanderer['want_amt']} {wanderer['want']}",
                   scr.C_YELLOW)
        scr.addstr(stdscr, 7, 2, "t) trade   q) send them on", scr.C_DIM)
        stdscr.refresh()

        key = scr.get_key(stdscr)
        if key in ("t", "T"):
            return world.resolve_trade(gs, wanderer, accept=True)
        elif key in ("q", "Q", "ESC"):
            return world.resolve_trade(gs, wanderer, accept=False)


# ── Flash collector ───────────────────────────────────────────

def _collect_flashes(flashes: list, *items) -> None:
    for item in items:
        if item:
            flashes.append(item)


# ── Splash screen ─────────────────────────────────────────────

def show_splash(stdscr: curses.window, gs: GameState,
                days: int = 0, decay_msg: str | None = None) -> None:
    from ui.splash import draw_splash
    draw_splash(stdscr, gs, days, decay_msg)
    scr.get_key(stdscr)


# ── Title screen ──────────────────────────────────────────────

def title_screen(stdscr: curses.window) -> GameState:
    stdscr.erase()
    scr.addstr(stdscr, 3, 4, "a quiet current",
               scr.C_BRIGHT_WHITE, bold=True)
    scr.addstr(stdscr, 5, 4, "something remains.", scr.C_DIM)
    scr.addstr(stdscr, 7, 4, "name this place: ", scr.C_NORMAL)
    stdscr.refresh()

    name = scr.prompt_text(stdscr, 7, 4, "name this place: ", max_len=24)
    if not name:
        name = "the settlement"

    gs = GameState(settlement_name=name)
    return gs


# ── Entry point ───────────────────────────────────────────────

def main(stdscr: curses.window) -> None:
    scr.init_colors()
    curses.curs_set(0)
    stdscr.keypad(True)

    gs = load_game()

    if gs:
        days = days_since_last_seen(gs)
        gs.days_founded += max(0, days)
        decay_msg = pan.apply_decay(gs, days)
        show_splash(stdscr, gs, days, decay_msg)
    else:
        gs = title_screen(stdscr)
        save_game(gs)
        show_splash(stdscr, gs)

    game_loop(stdscr, gs)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
