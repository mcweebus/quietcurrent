# ui/screen.py
# Curses initialization, color pairs, drawing primitives.

import curses

# Color pair IDs
C_NORMAL      = 0
C_DIM         = 1
C_BOLD        = 2
C_RED         = 3
C_GREEN       = 4
C_YELLOW      = 5
C_CYAN        = 6
C_MAGENTA     = 7
C_WHITE       = 8
C_BRIGHT_RED  = 9
C_BRIGHT_GREEN  = 10
C_BRIGHT_YELLOW = 11
C_BRIGHT_CYAN   = 12
C_BRIGHT_WHITE  = 13

# Plot state → color pair
PLOT_COLORS = {
    "E": C_DIM,
    "D": C_YELLOW,
    "P": C_GREEN,
    "G": C_BRIGHT_GREEN,
    "R": C_BRIGHT_YELLOW,
    "W": C_RED,
    "X": C_DIM,
}

# Soil quality → color pair
SOIL_COLORS = [None, C_RED, C_RED, C_YELLOW, C_GREEN, C_BRIGHT_GREEN]

# Moisture → color pair
MOIST_COLORS = [C_DIM, C_CYAN, C_CYAN, C_BRIGHT_CYAN, C_BRIGHT_CYAN, C_BRIGHT_CYAN]

# Mood → color pair
MOOD_COLORS = {
    3: C_BRIGHT_GREEN,
    2: C_GREEN,
    1: C_YELLOW,
    0: C_RED,
}


def init_colors() -> None:
    """Initialize all color pairs. Call after curses.start_color()."""
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(C_DIM,          curses.COLOR_BLACK,   -1)
    curses.init_pair(C_RED,          curses.COLOR_RED,     -1)
    curses.init_pair(C_GREEN,        curses.COLOR_GREEN,   -1)
    curses.init_pair(C_YELLOW,       curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_CYAN,         curses.COLOR_CYAN,    -1)
    curses.init_pair(C_MAGENTA,      curses.COLOR_MAGENTA, -1)
    curses.init_pair(C_WHITE,        curses.COLOR_WHITE,   -1)
    curses.init_pair(C_BRIGHT_RED,   curses.COLOR_RED,     -1)
    curses.init_pair(C_BRIGHT_GREEN, curses.COLOR_GREEN,   -1)
    curses.init_pair(C_BRIGHT_YELLOW,curses.COLOR_YELLOW,  -1)
    curses.init_pair(C_BRIGHT_CYAN,  curses.COLOR_CYAN,    -1)
    curses.init_pair(C_BRIGHT_WHITE, curses.COLOR_WHITE,   -1)


def attr(pair_id: int, bold: bool = False, dim: bool = False) -> int:
    a = curses.color_pair(pair_id)
    if bold: a |= curses.A_BOLD
    if dim:  a |= curses.A_DIM
    return a


def addstr(win, y: int, x: int, text: str,
           pair: int = C_NORMAL, bold: bool = False, dim: bool = False) -> None:
    """Safe addstr — silently ignores out-of-bounds writes."""
    try:
        win.addstr(y, x, text, attr(pair, bold=bold, dim=dim))
    except curses.error:
        pass


def addch(win, y: int, x: int, ch: str,
          pair: int = C_NORMAL, bold: bool = False, dim: bool = False) -> None:
    try:
        win.addch(y, x, ch, attr(pair, bold=bold, dim=dim))
    except curses.error:
        pass


def clear_line(win, y: int, width: int) -> None:
    try:
        win.move(y, 0)
        win.clrtoeol()
    except curses.error:
        pass


def draw_hline(win, y: int, x: int, ch: str, length: int,
               pair: int = C_DIM) -> None:
    for i in range(length):
        addch(win, y, x + i, ch, pair)


def get_key(stdscr) -> str:
    """Read a keypress and return a normalized string."""
    try:
        key = stdscr.get_wch()
    except curses.error:
        return ""

    if isinstance(key, int):
        mapping = {
            curses.KEY_UP:    "UP",
            curses.KEY_DOWN:  "DOWN",
            curses.KEY_LEFT:  "LEFT",
            curses.KEY_RIGHT: "RIGHT",
            curses.KEY_BACKSPACE: "BACKSPACE",
            27: "ESC",
        }
        return mapping.get(key, "")

    return str(key)


def prompt_text(stdscr, y: int, x: int, prompt: str,
                max_len: int = 30) -> str:
    """Simple line-input prompt. Returns stripped string."""
    curses.echo()
    curses.curs_set(1)
    addstr(stdscr, y, x, prompt)
    stdscr.refresh()
    buf = stdscr.getstr(y, x + len(prompt), max_len)
    curses.noecho()
    curses.curs_set(0)
    return buf.decode("utf-8", errors="ignore").strip()
