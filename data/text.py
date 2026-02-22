# data/text.py
# All flavor text, resident/wanderer definitions.
# No game logic here — pure data.

# --- Ancestral name -----------------------------------------

ANCESTRAL_FRAGMENTS = ["ver", "dan", "sol", "ith", "an"]
# Full name: Verdansolith-an

ANCESTRAL_TEND_MILESTONES = [5, 15, 30, 50, 75]

# --- Panel --------------------------------------------------

PANEL_NEGLECTED_TEND = [
    "you work at the surface. the grime is older than it looks.",
    "your hands come away grey. the glass underneath is still hidden.",
    "something shifts. or maybe it doesn't. hard to say.",
    "the panel takes the attention without giving much back.",
    "layers. there are more layers than you expected.",
    "you keep at it. the light changes, but that might be the clouds.",
]

PANEL_CLEAN_TRANSITION = (
    "the grime comes away in strips. underneath, the glass is intact."
)

PANEL_CONNECT_NEED_SCRAP = (
    "you need scrap to connect it. there may be some nearby."
)

PANEL_CONNECT_TRANSITION = (
    "you strip wire from the wall and connect what you can. something flows."
)

PANEL_MAINTAIN_OK = [
    "the panel is in good shape. you check it over anyway.",
    "everything looks right. the output holds steady.",
    "clean contacts, clear glass. you leave it to work.",
    "the hum is even. nothing to fix today.",
]

PANEL_DESCRIPTIONS = {
    "neglected": "a solar panel leans against a crumbling wall. its surface is thick with grime.",
    "cleaned":   "a solar panel leans against a crumbling wall. the glass is clear now. it catches the light faintly.",
    100: "the panel works steadily. the hum is even.",
    75:  "the panel works, but something is slightly off.",
    50:  "the output is reduced. the panel needs attention.",
    25:  "the panel struggles. several things need fixing.",
    0:   "barely anything is coming through. the panel is in poor shape.",
}

PANEL_FLASH = {
    "dust":      "the glass looks hazy in the strong light.",
    "wire":      "the connection sounds different — a faint intermittent hum.",
    "debris":    "something has settled around the base of the panel.",
    "connector": "a small creak from the panel. something working itself loose.",
}

PANEL_MAINTENANCE_RESULTS = {
    "dust":      "you wipe the glass down. the surface clears. output improves.",
    "wire":      "you press the connector home. the hum steadies.",
    "debris":    "you kick the debris clear. the base is clean.",
    "connector": "you swap the connector out. the creak is gone. (-1 scrap)",
    "connector_no_scrap": "you need a piece of scrap to replace it.",
}

PANEL_CONDITION_LABELS = {
    "dust":      "dust on the glass",
    "wire":      "a loose wire",
    "debris":    "debris around the base",
    "connector": "a worn connector",
}

# --- Weather ------------------------------------------------

WEATHER_SYMBOLS = {
    "sunny":  "☀",
    "cloudy": "☁",
    "rainy":  "☂",
    "windy":  "~",
}

# --- Exploration --------------------------------------------

EXPLORE_LOOT_SCRAP = [
    "salvaged wire and fittings.",
    "a bent bracket and two good bolts.",
    "sheet metal, workable.",
]

EXPLORE_LOOT_WATER = [
    "a sealed bottle, still good.",
    "water pooled in clean plastic.",
    "condensation, carefully gathered.",
]

EXPLORE_LOOT_SEEDS = [
    "a paper envelope. seeds, probably viable.",
    "dried pods. worth planting.",
    "a small cache, left deliberately.",
]

EXPLORE_ENCOUNTERS_SAFE = [
    "something moves in the peripheral dark. then doesn't.",
    "a cold firepit. someone was here. isn't now.",
    "a noise you can't place. you wait. it stops.",
    "you are watched. you don't know by what. it passes.",
    "a door, half open. you don't go in.",
    "footprints in soft ground. recent. heading away.",
]

EXPLORE_ENCOUNTERS_HARM = [
    "a collapse. debris catches your shoulder.",
    "the footing gives. you catch yourself but not cleanly.",
    "something in the undergrowth. you move fast. not fast enough.",
]

EXPLORE_HIGH_GROUND = [
    "from the high ground you can see for a long way. nothing moves.",
    "the view is wide. the settlement is visible, small and far.",
    "wind up here. it clears your head.",
]

EXPLORE_DEPART = [
    "you leave {name}.",
    "the path out is overgrown. you follow where the light is brightest.",
    "you head away from the panel, into whatever is out there.",
    "the air is different outside. harder to read.",
    "you go. the settlement waits.",
]

EXPLORE_RETURN = "you return to {name}"
EXPLORE_RETURN_EMPTY = "empty-handed"

EXPLORE_DEATH = [
    "you don't make it back.",
    "not this time.",
    "but the ground remembers.",
    "{name} waits.",
]

# --- Gather -------------------------------------------------

GATHER_DEPART = [
    "you leave {name} and walk until the ground changes.",
    "the path out is overgrown. you follow where the light is brightest.",
    "you head away from the panel, into whatever is out there.",
    "the air is different outside. harder to read.",
    "you go. the settlement waits.",
]

# --- Passives -----------------------------------------------

PASSIVE_RAIN_CATCHER = "the rain catcher has collected something."
PASSIVE_GARDEN_BED   = "the garden bed yields a little."

# --- Wanderers ----------------------------------------------

WANDERERS = [
    {
        "name":  "Sable",
        "desc":  "travels with something that isn't there anymore. still seems to expect it.",
        "give":  "scrap", "give_amt": 2,
        "want":  "water", "want_amt": 1,
        "stay_chance": 0.3,
        "fragment": True,
    },
    {
        "name":  "Drift",
        "desc":  "knows seventeen ways to approach a problem. won't say where that comes from.",
        "give":  "water", "give_amt": 3,
        "want":  "seeds", "want_amt": 1,
        "stay_chance": 0.25,
        "fragment": False,
    },
    {
        "name":  "Fen",
        "desc":  "marks every surface they pass with a small impression. old habit, or so it seems.",
        "give":  "seeds", "give_amt": 3,
        "want":  "scrap", "want_amt": 1,
        "stay_chance": 0.35,
        "fragment": True,
    },
    {
        "name":  "Lace",
        "desc":  "arrived during the last rain. hasn't said much about where from.",
        "give":  "water", "give_amt": 2,
        "want":  "scrap", "want_amt": 1,
        "stay_chance": 0.2,
        "fragment": False,
    },
    {
        "name":  "Crest",
        "desc":  "carries very little. moves like something that has been moving for a long time.",
        "give":  "scrap", "give_amt": 3,
        "want":  "water", "want_amt": 2,
        "stay_chance": 0.2,
        "fragment": False,
    },
    {
        "name":  "Weft",
        "desc":  "arrived without announcement. the space around the panel feels more settled since.",
        "give":  "scrap", "give_amt": 2,
        "want":  "seeds", "want_amt": 2,
        "stay_chance": 0.4,
        "fragment": True,
    },
    {
        "name":  "Tuck",
        "desc":  "found the rain catcher before you pointed it out. has been near it since.",
        "give":  "seeds", "give_amt": 2,
        "want":  "water", "want_amt": 1,
        "stay_chance": 0.35,
        "fragment": False,
    },
    {
        "name":  "Pale",
        "desc":  "quiet in a way that feels deliberate. takes up very little of anything.",
        "give":  "water", "give_amt": 1,
        "want":  "scrap", "want_amt": 1,
        "stay_chance": 0.3,
        "fragment": True,
    },
    {
        "name":  "Thresh",
        "desc":  "arrived with more than expected. or less. the accounting is unclear.",
        "give":  "scrap", "give_amt": 3,
        "want":  "seeds", "want_amt": 1,
        "stay_chance": 0.25,
        "fragment": False,
    },
    {
        "name":  "Reed",
        "desc":  "has strong opinions about where things belong. not always wrong about it.",
        "give":  "seeds", "give_amt": 4,
        "want":  "water", "want_amt": 2,
        "stay_chance": 0.3,
        "fragment": True,
    },
]

WANDERER_TRADE_ACCEPT = [
    "they take it without ceremony. you take what's offered.",
    "the exchange is brief. both sides seem satisfied.",
    "done. simpler than expected.",
]

WANDERER_TRADE_DECLINE = [
    "{name} nods and moves on.",
    "you watch {name} go. the settlement feels the same size.",
    "{name} doesn't seem offended. people pass through.",
]

WANDERER_STAY = "{name} stays."
WANDERER_LEAVE = "{name} moves on before dark."
WANDERER_NO_ROOM = "{name} considers it. there isn't room."

WANDERER_FRAGMENT = (
    "{name} pauses before leaving. "
    "'this place has a name,' they say. '{fragment}.'"
)

# --- Residents ----------------------------------------------

RESIDENTS = {
    "Weft": {
        "desc":     "arrived without announcement. the space around the panel feels more settled since.",
        "primary":  "panel_efficiency_75",
        "secondary":"weather_sunny",
        "effect":   "clear_dust",
        "farewell": "the panel area feels slightly less certain than it did.",
    },
    "Tuck": {
        "desc":     "found the rain catcher before you pointed it out. has been near it since.",
        "primary":  "water_or_rain",
        "secondary":"weather_rainy",
        "effect":   "water_bonus",
        "farewell": "the rain catcher still works. something is missing from near it.",
    },
    "Sable": {
        "desc":     "travels with something that isn't there anymore. still seems to expect it.",
        "primary":  "residents_2",
        "secondary":"garden_active_2",
        "effect":   "community_draw",
        "farewell": "Sable has gone. no announcement. just the absence.",
    },
    "Fen": {
        "desc":     "marks every surface they pass with a small impression. old habit, or so it seems.",
        "primary":  "garden_active_3",
        "secondary":"weeds_low",
        "effect":   "soil_improve",
        "farewell": "the small marks on the surfaces remain. Fen does not.",
    },
    "Drift": {
        "desc":     "knows seventeen ways to approach a problem. won't say where that comes from.",
        "primary":  "always",
        "secondary":"panel_efficiency_50",
        "effect":   "weather_nudge",
        "farewell": "Drift moved on. this was probably always temporary.",
    },
    "Pale": {
        "desc":     "quiet in a way that feels deliberate. takes up very little of anything.",
        "primary":  "panel_efficiency_50",
        "secondary":"residents_3",
        "effect":   "connector_protect",
        "farewell": "Pale is no longer here. the quiet is a different kind now.",
    },
    "Thresh": {
        "desc":     "arrived with more than expected. or less. the accounting is unclear.",
        "primary":  "residents_2",
        "secondary":"weather_not_windy",
        "effect":   "catalyst",
        "farewell": "Thresh left without taking much. or left taking everything. hard to tell.",
    },
    "Reed": {
        "desc":     "has strong opinions about where things belong. not always wrong about it.",
        "primary":  "garden_active_5",
        "secondary":"water_2",
        "effect":   "seed_gen",
        "farewell": "Reed is gone. the garden opinions go with them.",
    },
}

RESIDENT_INTERACTIONS = {
    frozenset(["Weft", "Tuck"]):
        "something in the corner near the rain catcher looks more settled than usual.",
    frozenset(["Sable", "Thresh"]):
        "Thresh and Sable occupy different parts of the space. the arrangement seems intentional.",
    frozenset(["Fen", "Reed"]):
        "Fen and Reed seem to disagree about something near the garden. it doesn't appear to matter.",
    frozenset(["Weft", "Pale"]):
        "the panel has been particularly stable lately. something about the attention it's getting.",
    frozenset(["Tuck", "Reed"]):
        "the moisture around the garden plots is higher than the rain catcher alone would explain.",
    frozenset(["Drift", "Sable"]):
        "Drift and Sable were in the same area earlier. the space felt briefly different.",
}

MOOD_LABELS = {
    3: "settled",
    2: "present",
    1: "unsettled",
    0: "departing",
}

# --- Decay --------------------------------------------------

DECAY_MESSAGES = {
    "severe":   "things have slipped.",
    "moderate": "dust has settled.",
    "minor":    "time has passed.",
}

# --- Garden -------------------------------------------------

CROPS = {
    "sunflower": {
        "label":   "sunflower",
        "symbol":  "S",
        "speed":   1.4,    # growth rate multiplier
        "harvest": {"seeds": (2, 3)},   # (min, max) before bonus
        "desc":    "fast grower, yields seeds",
    },
    "squash": {
        "label":   "squash",
        "symbol":  "Q",
        "speed":   0.7,
        "harvest": {"seeds": (1, 2), "water": (1, 2)},
        "desc":    "slow, yields water and seeds",
    },
    "bean": {
        "label":   "bean",
        "symbol":  "B",
        "speed":   1.0,
        "harvest": {"seeds": (2, 3)},
        "soil_bonus": 1,
        "desc":    "medium, yields seeds, improves soil",
    },
}

# Garden messages
GARDEN_DIG_OK       = "you turn the earth. soil quality: {soil}."
GARDEN_DIG_WEEDS    = "clear the weeds first."
GARDEN_DIG_DONE     = "this plot is already worked."
GARDEN_PLANT_NONE   = "dig the plot first."
GARDEN_PLANT_NOSEED = "you have no seeds."
GARDEN_PLANT_OK     = "you press the seed into the earth. now it waits."
GARDEN_WATER_OK     = "the earth absorbs it. moisture: {moist}."
GARDEN_WATER_NONE   = "nothing here to water."
GARDEN_WATER_DRY    = "you have no water."
GARDEN_HARVEST_WAIT = "this plot isn't ready yet."
GARDEN_WEED_OK      = "weeds pulled. the ground is open again."
GARDEN_WEED_NONE    = "no weeds here."
GARDEN_COMPOST_NEED = "you need a compost pile first."
GARDEN_COMPOST_APPLY_OK   = "rich material worked into the earth. soil quality now {soil}."
GARDEN_COMPOST_APPLY_EMPTY= "the compost pile is empty. add to it first."
GARDEN_COMPOST_APPLY_NODIG= "dig this plot before applying compost."
GARDEN_COMPOST_ADD_OK     = "you add to the pile. it steams faintly. (compost: {level}/5)"
GARDEN_COMPOST_ADD_NONE   = "nothing to add to the pile right now."
GARDEN_ENTER        = "you step into the garden."
GARDEN_LEAVE        = "you leave the garden."

# Pollinator
POLLINATOR_PRESENT  = "✦ pollinators visiting"
POLLINATOR_BONUS    = "pollinator bonus"

# --- Buildings ----------------------------------------------

BUILDINGS = [
    {
        "key":   "junction_box",
        "label": "junction box",
        "cost":  {"scrap": 5},
        "desc":  "stores power between sessions",
        "built": [
            "you run wire along the wall, splice what you find.",
            "salvaged components. it shouldn't work. it does.",
        ],
    },
    {
        "key":   "rain_catcher",
        "label": "rain catcher",
        "cost":  {"scrap": 3},
        "desc":  "collects water passively",
        "built": [
            "corrugated sheet, angled. you wait. it works.",
            "the first drop sounds different when there's something to catch it.",
        ],
    },
    {
        "key":   "garden_bed",
        "label": "garden bed",
        "cost":  {"scrap": 4, "seeds": 2},
        "desc":  "a place to grow things",
        "built": [
            "broken ground, turned and bordered. something might grow here.",
            "you clear the space. the earth underneath is darker than expected.",
        ],
    },
    {
        "key":   "signal_beacon",
        "label": "signal beacon",
        "cost":  {"scrap": 8, "power": 10},
        "desc":  "draws others toward the settlement",
        "built": [
            "the hum starts low. it carries.",
            "you connect the last wire. something in the air changes.",
        ],
    },
    {
        "key":   "compost_pile",
        "label": "compost pile",
        "cost":  {"scrap": 4},
        "desc":  "breaks down matter, improves soil",
        "built": [
            "you layer scraps, soil, and dry matter into a corner. it will break down in time.",
        ],
    },
]

# --- Title / splash -----------------------------------------

TITLE_LINES = [
    "a quiet current",
    "",
    "something remains.",
    "you are in {name}.",
]

RETURN_LINES = {
    0:   "you are back in {name}.",
    1:   "you return to {name} after a day away.",
    "n": "you return to {name}. {days} days have passed.",
}

ANCESTRAL_MILESTONE = (
    "something scratched into the wall catches your eye. it reads: {fragment}."
)

ANCESTRAL_DEATH = (
    "something remains of what was known. {fragment}."
)
