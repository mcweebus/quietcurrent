# A Quiet Current — Design Document
# Version 0.2 / February 2026
# Paste this into new sessions to restore full context.

---

## What this is

A terminal-based settlement management game. The player tends a solar panel,
gathers resources, builds structures, cultivates a garden, and attracts a
community. The aesthetic is cozy post-apocalyptic rebuilding — solarpunk in
tone, quiet in pace.

The game is currently being built in Python (curses). A working bash prototype
exists but was abandoned for the Python port. The Python project structure is:

    quietcurrent_py/
    ├── main.py               # entry point, game loop, menus
    ├── engine/
    │   ├── state.py          # GameState dataclass, save/load (JSON)
    │   ├── panel.py          # panel efficiency, weather, maintenance
    │   ├── garden.py         # 12×8 grid, crops, compost, pollinators
    │   ├── residents.py      # resident system, mood, effects
    │   └── world.py          # passives, wanderers, ancestral milestones
    ├── ui/
    │   ├── screen.py         # curses setup, color pairs, primitives
    │   ├── garden_view.py    # garden grid renderer
    │   ├── explore_view.py   # exploration map renderer
    │   └── splash.py         # launch splash screen
    └── data/
        └── text.py           # ALL flavor text, definitions, no logic

Save file: ~/.quietcurrent/save.json
Windows launcher: play.bat (checks for Python, friendly error if missing)

---

## The central design secret

**There are no human beings in this game.**

All life — the player character, wanderers, residents — is plant or fungal in
nature. The game never lies to the player, but it never confirms this either.
The writing conceals the fact through careful language. The player assumes a
cozy human post-apocalypse. The reveal happens through accumulation — a word
used that humans wouldn't use about themselves, a behavior that takes a moment
to parse, a relationship that doesn't map onto human norms.

This reveal cannot be a moment. It must be a dawning. No cutscene, no lore
dump. The text has been consistent all along and the player was the one
assuming.

---

## Writing discipline

The single most important constraint in the entire project.

**Never lie. Never confirm.**

Rules:
- No pronouns that carry physical assumptions. "They" works. "Their hands"
  does not — we haven't established hands. "They work at it" is fine.
  "They wipe their brow" is not.
- Resident behaviors described through presence and effect, not action.
  A resident doesn't "fix the wire" — "the wire holds better since Weft
  arrived." A resident doesn't "water the garden" — "the moisture around
  plot C3 is consistently higher near where Tuck has settled."
- The settlement responds. The panel hums differently. The soil in one corner
  is richer. These things happen without anyone being seen doing them.
- Avoid painted corners. "Rooted in place for a season" answers the question.
  "Hasn't moved from that spot in weeks, but seems fine" leaves it open.
- No human physiology: no hunger, no sleep, no shelter complaints. Residents
  respond to moisture, light quality, soil conditions.
- Mood labels chosen to avoid implying biology: "settled", "present",
  "unsettled", "departing" — not "happy", "hungry", "sick", "dead".

---

## The panel

Central object. The player's first relationship. Progression:

    neglected → cleaned → connected

- Neglected: thick grime, no power generation. Tends required to clean.
- Cleaned: glass clear, no power yet. Needs 2 scrap to connect.
- Connected: generates power passively. Efficiency 0–100%.

**Efficiency system:**
Four maintenance conditions, each degrading efficiency by 25%:
- Dust on glass — builds in sunny weather (8% chance/action)
- Loose wire — loosens in rain (10% chance/action)
- Debris at base — accumulates in wind (9% chance/action)
- Worn connector — slow wear, any weather (2% chance/action, halved if Pale
  is a resident)

Maintenance submenu opens when tending a connected panel with active
conditions. Dust/wire/debris are free to fix. Connector costs 1 scrap.

Passive power rate by efficiency:
- 100–75%: 1 power every 5 actions (+1 bonus with junction box)
- 74–50%:  1 power every 7 actions
- 49–25%:  1 power every 10 actions
- 24–0%:   1 power every 15 actions

Panel description changes with efficiency, using flavor text that implies
something is wrong without naming it.

---

## Weather

Four states: sunny, cloudy, rainy, windy.
Changes every 6–12 actions. Drives panel degradation.
Displayed as a symbol on the status screen and splash.
Future: will affect garden moisture.

Weather symbols: ☀ ☁ ☂ ~

---

## Garden

12×8 grid (96 plots). Cursor navigation with arrow keys.

**Plot states:** E(empty) D(dug) P(planted) G(growing) R(ready) W(weedy) X(depleted)

**Crops:**
- Sunflower: fast growth (1.4×), yields 2–3 seeds
- Squash: slow growth (0.7×), yields 1–2 seeds + 1–2 water
- Bean: medium growth (1.0×), yields 2–3 seeds, +1 soil quality on harvest

**Soil quality 1–5, moisture 0–5.** Growth rate = soil × 4 + moisture × 2 per tick.
Moisture evaporates each tick. Weeds spread at 1% per empty/dug plot per action.
Depleted plots recover to empty at 8% chance per action.

**Compost pile (structure, 4 scrap):**
- Add scrap to pile: `+` or `=` key (-1 scrap, +1 compost level, max 5)
- Apply to dug plot: `k` key (-1 compost level, +1 soil quality)

**Pollinators:**
- Spawn when 2+ active plots, up to 3 at once, displayed as ✦
- Wander randomly, 10% chance to leave per action
- Harvesting with pollinator on/adjacent to plot: +1 yield bonus

**Garden actions:** d(dig) p(plant) w(water) h(harvest) c(clear weeds)
k(apply compost) +(add to compost) q(leave)

---

## Structures

Built from the main menu once panel is connected.

| Structure      | Cost           | Effect                              |
|----------------|----------------|-------------------------------------|
| Junction box   | 5 scrap        | Stores power, reduces decay         |
| Rain catcher   | 3 scrap        | +1 water every 4 actions passively  |
| Garden bed     | 4 scrap+2 seeds| Unlocks garden                      |
| Signal beacon  | 8 scrap+10 pwr | Enables wanderer arrivals           |
| Compost pile   | 4 scrap        | Unlocks composting                  |

---

## Wanderers

Arrive when signal beacon is built. One at a time.
Each offers a trade (give resource, want resource).
After trade, small chance they stay as a resident.
Some carry ancestral name fragments.

10 named wanderers: Sable, Drift, Fen, Lace, Crest, Weft, Tuck, Pale,
Thresh, Reed. All described without confirming species or physiology.

---

## Residents

Up to 8. Each retains their wanderer identity. Persist between sessions.

**Mood system:** 3(thriving) → 2(stable) → 1(uneasy) → 0(departing)
Each action tick: primary condition evaluated (+1 if met, -1 if not),
secondary sensitivity applies additional ±1.
At mood 0: farewell line surfaces, resident gone next session.

**Resident roster and effects:**

| Name   | Primary condition      | Secondary          | Passive effect              |
|--------|------------------------|--------------------|-----------------------------|
| Weft   | panel efficiency ≥75%  | weather sunny      | Occasionally clears dust    |
| Tuck   | water≥3 or raining     | weather rainy      | Water bonus during rain     |
| Sable  | 2+ residents present   | 2+ active plots    | Boosts wanderer arrival +4  |
| Fen    | 3+ active plots        | weeds ≤1           | Improves random soil quality |
| Drift  | always met             | efficiency ≥50%    | Nudges weather duration     |
| Pale   | efficiency ≥50%        | 3+ residents       | Halves connector wear rate  |
| Thresh | 2+ residents present   | weather not windy  | Boosts wanderer arrival +2  |
| Reed   | 5+ active plots        | water ≥2           | Passive seed generation     |

**6 interaction pairs** (rare, ~8% chance/tick, easy to miss):
Weft+Tuck, Sable+Thresh, Fen+Reed, Weft+Pale, Tuck+Reed, Drift+Sable.
Lines describe the effect, never announce the interaction.

---

## Ancestral name

Verdansolith-an. Revealed one fragment at a time through:
- Tend milestones: 5, 15, 30, 50, 75 tends
- Wanderer trade (some wanderers carry fragments)
- Death on exploration

The name accumulates: ver → verdan → verdansol → verdansolith → verdansolith-an.
Displayed in the splash screen as "known name" once any fragment is revealed.

---

## Exploration

Separate screen. 36×14 procedurally generated map per visit.
Arrow key movement. Terrain: open ground, walls, water, high ground, loot.
HP: 5. Encounters (12% chance per step): mostly flavor, some damage.
Loot caches yield scrap, water, or seeds.
Death: resources halved, panel degrades, ancestral fragment may be revealed.

---

## Splash screen

Shown on every launch. Two columns:
- Left: ASCII settlement scene (panel state, structures present, garden growth
  stage, resident dots). Scene evolves with game state.
- Right: settlement name, days away, weather, garden health bar + counts,
  resources, resident count, known ancestral name.

---

## Time / decay

Real-world time elapsed since last session:
- 1–2 days: minor power loss (if no junction box)
- 3–5 days: moderate power decay
- 6–13 days: significant power + water loss
- 14+ days: severe decay across all resources, panel may degrade state

---

## Known gaps / next sprint priorities

1. **Maintenance submenu** — currently auto-applies first condition in
   main.py's do_tend(). Needs a proper curses menu so player chooses which
   condition to address.

2. **Wanderer stay prompt** — stay/leave currently resolved automatically
   after trade. Should offer explicit "ask them to stay" option.

3. **Exploration persistence** — map regenerates each visit. Future: visited
   areas remembered, map expands over time.

4. **Flower crop** — separate from food crops. Aesthetic, attracts visitors
   more frequently. Planned as a Sprint after maintenance menu.

5. **Robot gardener** — mid-game structure. Player programs simple automation
   logic to tend plots while away. Intended as a clean module boundary.
   Deferred until core loop is stable.

6. ~~**Weather affecting garden**~~ — done. Rain: 60% chance +1 moisture
   per exposed plot (D/P/G/R), no evaporation. Sunny/windy: evaporate 2/tick
   instead of 1. Cloudy: normal (evaporate 1).

7. **Windows terminal Unicode** — curses on Windows via python-windows-curses
   package. Test ✦ ☀ ☁ ☂ █ ░ rendering on Windows Terminal specifically.

---

## Tone reference

The game is quiet. It does not celebrate. It does not mourn.
It notices things.

"the panel adds to what it can."
"a corner of the garden looks different. the soil there is richer."
"Sable has gone. no announcement. just the absence."
"something remains of what was known."

All prose lowercase except proper nouns (settlement name, resident names).
Short sentences. No exclamation points. Observations, not directions.
