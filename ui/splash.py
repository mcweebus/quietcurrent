# ui/splash.py
# Launch splash screen. Left: ASCII settlement scene.
# Right: garden health and key stats.

import curses
from engine.state import GameState, GARDEN_SIZE
from engine.garden import network_summary
from engine import panel as pan
from ui import screen as scr
from data import text as txt


def draw_splash(stdscr: curses.window, gs: GameState,
                days: int = 0, decay_msg: str | None = None) -> None:
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    scene = _build_scene(gs)
    status = _build_status(gs, days, decay_msg)

    for i, (scene_line, status_line) in enumerate(zip(scene, status)):
        row = i + 1
        if row >= height - 1:
            break
        # Scene (left, col 2)
        _draw_rich_line(stdscr, row, 2, scene_line)
        # Status (right, col 38)
        _draw_rich_line(stdscr, row, 38, status_line)

    # Press any key
    scr.addstr(stdscr, min(len(scene) + 2, height - 2), 2,
               "press any key", scr.C_DIM)
    stdscr.refresh()


# ── Scene builder ─────────────────────────────────────────────
# Each element is a list of (text, pair, bold) tuples.

def _build_scene(gs: GameState) -> list:
    lines = [[] for _ in range(14)]

    # Signal beacon
    if gs.has_signal_beacon:
        lines[0] = [("                    ", scr.C_NORMAL, False),
                    (")))  ", scr.C_CYAN, False)]
        lines[1] = [("                    |", scr.C_CYAN, False)]

    # Panel
    panel_pair = scr.C_DIM
    panel_sym  = "[:::::]"
    if gs.panel_state == "cleaned":
        panel_pair = scr.C_YELLOW
    elif pan.panel_connected(gs):
        panel_pair = scr.C_BRIGHT_YELLOW
        panel_sym  = "[#####]"

    lines[2] = [("   ", scr.C_NORMAL, False),
                (panel_sym, panel_pair, gs.panel_state not in ("neglected",)),
                ("  ", scr.C_NORMAL, False)]
    if pan.panel_connected(gs):
        lines[2].append(("~", scr.C_BRIGHT_YELLOW, False))
    lines[3] = [("   |-----|", scr.C_DIM, False)]

    # Junction box
    if gs.has_junction_box:
        lines[4] = [("   |  ", scr.C_GREEN, False),
                    ("----[+]", scr.C_GREEN, False)]
    else:
        lines[4] = [("   |", scr.C_GREEN, False)]

    # Rain catcher
    if gs.has_rain_catcher:
        lines[5] = [("   |             ", scr.C_GREEN, False),
                    ("/\\", scr.C_CYAN, False)]
        lines[6] = [("   |            ", scr.C_GREEN, False),
                    ("(~~)", scr.C_CYAN, False)]
    else:
        lines[5] = [("   |", scr.C_GREEN, False)]

    # Garden / flowers
    if gs.has_garden_bed:
        summ = network_summary(gs) if gs.garden_initialized else {}
        active = summ.get("connected", 0) + summ.get("hypha", 0)

        if active >= 4:
            lines[7] = [
                ("  ", scr.C_NORMAL, False),
                ("*", scr.C_BRIGHT_YELLOW, True),
                ("  ", scr.C_NORMAL, False),
                ("^", scr.C_MAGENTA, False),
                ("  ", scr.C_NORMAL, False),
                ("*", scr.C_BRIGHT_RED, True),
                ("  ", scr.C_NORMAL, False),
                ("*", scr.C_BRIGHT_YELLOW, True),
                ("  ", scr.C_NORMAL, False),
                ("*", scr.C_BRIGHT_GREEN, True),
            ]
            lines[8] = [
                (" ", scr.C_NORMAL, False),
                ("(|)", scr.C_BRIGHT_YELLOW, False),
                (" ", scr.C_NORMAL, False),
                ("|", scr.C_MAGENTA, False),
                (" ", scr.C_NORMAL, False),
                ("(|)", scr.C_BRIGHT_RED, False),
                (" ", scr.C_NORMAL, False),
                ("|", scr.C_BRIGHT_YELLOW, False),
                (" ", scr.C_NORMAL, False),
                ("(|)", scr.C_BRIGHT_GREEN, False),
            ]
            lines[9] = [
                ("  ", scr.C_NORMAL, False),
                ("|", scr.C_GREEN, False),
                ("  ", scr.C_NORMAL, False),
                ("|", scr.C_GREEN, False),
                ("  ", scr.C_NORMAL, False),
                ("|", scr.C_GREEN, False),
                ("  ", scr.C_NORMAL, False),
                ("|", scr.C_GREEN, False),
                ("  ", scr.C_NORMAL, False),
                ("|", scr.C_GREEN, False),
            ]
        elif active >= 1:
            lines[7] = [("        ", scr.C_NORMAL, False),
                        ("*", scr.C_BRIGHT_YELLOW, True),
                        ("      ", scr.C_NORMAL, False),
                        ("^", scr.C_MAGENTA, False)]
            lines[8] = [("  ", scr.C_NORMAL, False),
                        (",", scr.C_DIM, False),
                        ("   ", scr.C_NORMAL, False),
                        ("|", scr.C_BRIGHT_YELLOW, False),
                        ("   ", scr.C_NORMAL, False),
                        (",", scr.C_DIM, False),
                        ("   ", scr.C_NORMAL, False),
                        ("|", scr.C_MAGENTA, False)]
            lines[9] = [("  ", scr.C_NORMAL, False),
                        ("|   |   |   |", scr.C_GREEN, False)]
        else:
            lines[7] = [("  ", scr.C_DIM, False),
                        (". . . . . . .", scr.C_DIM, False)]
            lines[8] = [("  ", scr.C_NORMAL, False),
                        ("| | | | | | |", scr.C_GREEN, False)]

        if gs.has_compost_pile:
            lines[9] = lines[9] + [("  ", scr.C_NORMAL, False),
                                    ("[~]", scr.C_DIM, False)]

    # Flower garden
    if gs.has_flower_garden and gs.flower_garden_init:
        from engine.flowers import FLOWERS
        blooming = [s for s in gs.flowers if s["state"] == "F"]

        if not blooming:
            flower_seg = [("  ", scr.C_NORMAL, False),
                          (". . .", scr.C_DIM, False)]
        else:
            flower_seg = [("  ", scr.C_NORMAL, False)]
            for slot in blooming[:5]:
                spec = FLOWERS.get(slot["flower"], {})
                flower_seg.append((spec.get("bloom_sym", "*"),
                                   spec.get("color", scr.C_BRIGHT_YELLOW), True))
                flower_seg.append((" ", scr.C_NORMAL, False))

        if gs.has_garden_bed:
            lines[9] = lines[9] + flower_seg
        else:
            lines[7] = flower_seg

    # Ground
    lines[10] = [("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", scr.C_DIM, False)]

    # Residents as dots
    if gs.residents:
        dots = []
        for r in gs.residents[:6]:
            dots.append(("•", scr.C_BRIGHT_WHITE, False))
            dots.append((" ", scr.C_NORMAL, False))
        lines[11] = [(" ", scr.C_NORMAL, False)] + dots

    return lines


# ── Status builder ────────────────────────────────────────────

def _build_status(gs: GameState, days: int, decay_msg: str | None) -> list:
    lines: list = [[] for _ in range(14)]

    # Settlement name
    lines[0] = [(gs.settlement_name, scr.C_BRIGHT_WHITE, True)]

    # Return context
    if days > 0:
        context = f"away {days} day(s)."
        if decay_msg:
            context += f" {decay_msg}"
        lines[1] = [(context, scr.C_DIM, False)]
    else:
        lines[1] = [("you are here.", scr.C_DIM, False)]

    # Weather
    sym = txt.WEATHER_SYMBOLS.get(gs.weather, "?")
    lines[2] = [(f"{sym} {gs.weather}", scr.C_NORMAL, False)]

    # Garden
    lines[3] = []
    lines[4] = [("garden", scr.C_NORMAL, True)]

    if gs.garden_initialized and gs.garden:
        summ = network_summary(gs)
        connected = summ["connected"]
        mature    = summ["mature"]
        fruiting  = summ["fruiting"]
        hypha     = summ["hypha"]

        if connected + hypha > 0:
            lines[5] = [("network: ", scr.C_NORMAL, False),
                        (str(connected), scr.C_BRIGHT_GREEN, False),
                        (" nodes", scr.C_DIM, False)]
            lines[6] = [("mature ", scr.C_BRIGHT_GREEN, False),
                        (str(mature), scr.C_NORMAL, False),
                        ("  fruiting ", scr.C_BRIGHT_YELLOW, False),
                        (str(fruiting), scr.C_NORMAL, False),
                        ("  hypha ", scr.C_DIM, False),
                        (str(hypha), scr.C_NORMAL, False)]
        else:
            lines[5] = [("not yet inoculated", scr.C_DIM, False)]
    else:
        lines[5] = [("—", scr.C_DIM, False)]

    # Flower garden summary
    if gs.has_flower_garden and gs.flower_garden_init:
        from engine.flowers import flower_summary
        fsumm = flower_summary(gs)
        lines[7] = [("flowers  ", scr.C_NORMAL, True),
                    ("budding ",   scr.C_GREEN, False),
                    (str(fsumm["budding"]),   scr.C_NORMAL, False),
                    ("  blooming ", scr.C_BRIGHT_YELLOW, False),
                    (str(fsumm["flowering"]), scr.C_NORMAL, False)]
    else:
        lines[7] = []

    # Resources
    lines[8] = [("power ", scr.C_BRIGHT_YELLOW, False),
                (str(gs.power).ljust(4), scr.C_NORMAL, False),
                ("  water ", scr.C_CYAN, False),
                (str(gs.water), scr.C_NORMAL, False)]
    lines[9] = [("scrap ", scr.C_YELLOW, False),
                (str(gs.scrap).ljust(4), scr.C_NORMAL, False),
                ("  spores ", scr.C_BRIGHT_GREEN, False),
                (str(gs.spores).ljust(4), scr.C_NORMAL, False),
                ("  mycelium ", scr.C_MAGENTA, False),
                (str(gs.mycelium), scr.C_NORMAL, False)]

    # Residents
    if gs.residents:
        lines[10] = []
        lines[11] = [("residents ", scr.C_NORMAL, True),
                     (str(len(gs.residents)), scr.C_NORMAL, False)]

    # Ancestral
    if gs.ancestral_revealed > 0:
        from engine.world import get_ancestral_so_far
        frag = get_ancestral_so_far(gs)
        lines[12] = [("known name  ", scr.C_NORMAL, False),
                     (frag, scr.C_MAGENTA, False)]

    return lines


# ── Renderer ──────────────────────────────────────────────────

def _draw_rich_line(stdscr, row: int, start_col: int,
                    segments: list) -> None:
    col = start_col
    for segment in segments:
        text, pair, bold = segment
        scr.addstr(stdscr, row, col, text, pair, bold=bold)
        col += len(text)
