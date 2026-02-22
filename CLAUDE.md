# quietcurrent_py

Terminal settlement game in Python/curses. Cozy post-apocalyptic rebuilding.
Central design secret: all life is plant or fungal — never confirmed, never denied.

## Orientation

1. Read `DESIGN.md` for full spec, tone rules, and known gaps
2. Run `git log --oneline -10` to see recent work
3. Check memory file at `~/.claude/projects/-home-geoffrey-Downloads-Projects/memory/MEMORY.md`

## Architecture

- `engine/` — pure logic, no curses imports, mutate GameState, return strings
- `ui/` — curses rendering, imports from engine
- `data/text.py` — all flavor text and definitions, no logic
- `main.py` — game loop, menus, delegates to ui views
- Save: `~/.quietcurrent/save.json` (auto-migrates on load)

## Key rules

- New state fields with defaults auto-migrate old saves — just add them
- Writing discipline: never confirm the player is a plant/fungus, never lie
- All prose lowercase except proper nouns. No exclamation points.
- Tone: quiet, observational. "the panel adds to what it can."
