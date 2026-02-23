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
    "dust":               "you wipe the glass down. the surface clears. output improves.",
    "wire":               "you work the connection back into place. the hum steadies. (-1 scrap)",
    "debris":             "you lever the debris clear. the base is clean. (-1 scrap)",
    "connector":          "you swap the connector out. the creak is gone. (-1 scrap)",
    "wire_no_scrap":      "you need a piece of scrap to reseat it properly.",
    "debris_no_scrap":    "you'd need scrap to lever this clear.",
    "connector_no_scrap": "you need a piece of scrap to replace it.",
}

PANEL_CONDITION_LABELS = {
    "dust":      "dust on the glass",
    "wire":      "a loose wire",
    "debris":    "debris around the base",
    "connector": "a worn connector",
}

PANEL_MAINTAIN_SKIPPED = [
    "you look it over. the conditions remain.",
    "you note what needs doing. you'll get to it.",
    "you take stock of it. not today.",
]

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

EXPLORE_LOOT_SPORES = [
    "a small container. spores, still viable.",
    "dried fruiting bodies. worth inoculating.",
    "a wrapped cache, left deliberately.",
]

EXPLORE_ENCOUNTERS_SAFE = [
    # atmosphere — kept from original
    "something moves in the peripheral dark. then doesn't.",
    "a cold firepit. someone was here. isn't now.",
    "a noise you can't place. you wait. it stops.",
    "you are watched. you don't know by what. it passes.",
    # traces of others
    "traces in the soft ground. recent. heading away.",
    "you find where a wanderer passed. the signs are the kind you recognize.",
    "a structure half-reclaimed. you can't tell if the reclaiming is recent or very old.",
    # environmental sensing
    "the soil here is different. darker. you note it without stopping.",
    "light comes through at a low angle. something in you orients toward it.",
    "a dry stretch. the crossing takes more than it should. you make it.",
    "old contaminated ground. you know to go around it before you know you know.",
    "rain has pooled in the low places. you slow down near it.",
    # other organisms
    "traces of an old network, long dormant. the ground still holds the shape of it.",
    "something is fruiting nearby. you can tell without seeing it.",
    "spores in the air that aren't yours. something else is spreading.",
    "the rootlines of something large are still under the broken ground.",
    # distance from home
    "the connection thins out here. a different kind of quiet.",
    # reclaimed world
    "concrete cracked into sections. something grows in every crack. it knows what it's doing.",
]

EXPLORE_ENCOUNTERS_HARM = [
    # physical
    "a collapse. debris comes down without warning. you come away slower.",
    "the footing gives. the recovery costs something.",
    # contamination
    "treated ground. something in it is wrong. you don't pass through cleanly.",
    "standing water, but the wrong kind. you know before you're in it. the knowing comes too late.",
    # competition
    "something in the undergrowth. it isn't moving away. you do, and not cleanly.",
    # environment
    "a dry heat off a south-facing surface. prolonged. you come away diminished.",
]

EXPLORE_HIGH_GROUND = [
    "from the high ground you can see for a long way. nothing moves.",
    "the view is wide. the settlement is visible, small and far.",
    "wind up here. something about the exposure suits you.",
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
PASSIVE_GARDEN_BED   = "the garden bed yields a few spores."

# --- Tending frame ------------------------------------------

FRAME_INOCULATE = [
    "the frame found an empty patch. a spore has been pressed in.",
    "a new hypha started while you were away. the frame did it.",
    "something small has been inoculated. the frame chose its spot.",
]

FRAME_CLEAR = [
    "the weeds are gone from one corner. the frame worked while you were away.",
    "a patch has been cleared. the ground is open again.",
    "the frame cleared something. you notice it only after.",
]

FRAME_WATER = [
    "a dry patch has been watered. your stores are a little lower.",
    "the frame drew from your water. a plot that needed it has been tended.",
    "something was thirsty. the frame attended to it.",
]

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
        "want":  "spores", "want_amt": 1,
        "stay_chance": 0.25,
        "fragment": False,
    },
    {
        "name":  "Fen",
        "desc":  "marks every surface they pass with a small impression. old habit, or so it seems.",
        "give":  "mycelium", "give_amt": 2,
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
        "want":  "spores", "want_amt": 2,
        "stay_chance": 0.4,
        "fragment": True,
    },
    {
        "name":  "Tuck",
        "desc":  "found the rain catcher before you pointed it out. has been near it since.",
        "give":  "spores", "give_amt": 2,
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
        "want":  "spores", "want_amt": 1,
        "stay_chance": 0.25,
        "fragment": False,
    },
    {
        "name":  "Reed",
        "desc":  "has strong opinions about where things belong. not always wrong about it.",
        "give":  "spores", "give_amt": 4,
        "want":  "mycelium", "want_amt": 1,
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

WANDERER_TRADE_SKIP = [
    "no exchange. that's all right.",
    "you leave it.",
    "they don't press it.",
]

WANDERER_LINGER = [
    "they don't seem to be in a hurry.",
    "something keeps them near a moment longer.",
    "the silence between you isn't uncomfortable.",
    "they haven't started moving yet.",
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
    "Lace": {
        "desc":     "arrived during the last rain. hasn't said much about where from.",
        "primary":  "water_2",
        "secondary":"weather_rainy",
        "effect":   "mycelium_gen",
        "farewell": "Lace has gone. the rain, when it comes, feels less like it was expected.",
    },
    "Crest": {
        "desc":     "carries very little. moves like something that has been moving for a long time.",
        "primary":  "always",
        "secondary":"panel_efficiency_50",
        "effect":   "scrap_gen",
        "farewell": "Crest has moved on. that was probably always going to happen.",
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

# Network state display names
NETWORK_STATE_NAMES = {
    "E": "empty substrate",
    "H": "hypha",
    "N": "network node",
    "M": "mature",
    "F": "fruiting",
    "X": "decomposing",
    "W": "competing growth",
}

# Garden messages
GARDEN_INOCULATE_OK       = "you press the spore into the substrate. something begins."
GARDEN_INOCULATE_NONE     = "you have no spores."
GARDEN_INOCULATE_OCCUPIED = "something is already growing here."
GARDEN_WATER_OK           = "the substrate absorbs it. moisture: {moist}."
GARDEN_WATER_NONE         = "nothing here to water."
GARDEN_WATER_DRY          = "you have no water."
GARDEN_CLEAR_OK           = "the competing growth is cleared. the ground is open again."
GARDEN_CLEAR_NONE         = "no competing growth here."
GARDEN_ENRICH_OK          = "rich material worked into the substrate. soil quality now {soil}."
GARDEN_ENRICH_NONE        = "the compost pile is empty. add to it first."
GARDEN_ENRICH_NOT_EMPTY   = "only empty substrate can be enriched."
GARDEN_MYCELIUM_NONE      = "you have no mycelium."
GARDEN_FEED_OK            = "nutrients move through the network. soil quality now {soil}."
GARDEN_FEED_WRONG         = "only connected network can receive nutrients."
GARDEN_EXTEND_OK          = "the network extends into new ground."
GARDEN_EXTEND_WRONG       = "the network can only extend into empty ground."
GARDEN_EXTEND_LOW         = "you need two mycelium to extend the network."
GARDEN_SUPPRESS_OK        = "the network reclaims the ground."
GARDEN_SUPPRESS_WRONG     = "no competing growth here to suppress."
GARDEN_COMPOST_NEED       = "you need a compost pile first."
GARDEN_COMPOST_ADD_OK     = "you add to the pile. it steams faintly. (compost: {level}/5)"
GARDEN_COMPOST_ADD_NONE   = "nothing to add to the pile right now."
GARDEN_ENTER              = "you step into the garden."
GARDEN_LEAVE              = "you leave the garden."

# Network fruiting flash messages
NETWORK_FRUIT = [
    "the network fruits. something has formed.",
    "a fruiting body. the network is productive.",
    "something emerges from the substrate.",
    "the colony has produced something.",
    "a quiet bloom from the mycelium.",
]

# --- Flower Garden ------------------------------------------

FLOWER_ENTER          = "you step into the flower garden."
FLOWER_LEAVE          = "you leave the flower garden."
FLOWER_PLANTED        = "you press the {flower} into the soil."
FLOWER_PLANT_OCCUPIED = "something is already growing here."
FLOWER_UNLOCK         = "{name} brought something with them — seeds, pressed flat in a cloth."

FLOWER_VISIT_EMPTY = "the garden is quiet. nothing is in bloom yet."

FLOWER_VISIT_BLOOMING = [
    "something has opened.",
    "colour, unexpected.",
    "the bees will know before you do.",
    "quiet, and then — flowers.",
    "the garden has its own schedule.",
    "the oldest flowers are the ones you didn't plant.",
    "something opened overnight. you weren't watching.",
]

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
        "cost":  {"scrap": 4, "spores": 2},
        "desc":  "a place to tend the network",
        "built": [
            "broken ground, bordered and ready. something might take hold here.",
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
    {
        "key":      "reinforced_mounting",
        "label":    "reinforce the mounting",
        "cost":     {"scrap": 3},
        "desc":     "debris settles less at the base",
        "requires": None,
        "built": [
            "you brace the frame. it sits more solidly in the ground.",
            "less give in the base. the panel should weather wind better.",
        ],
    },
    {
        "key":      "deepened_catcher",
        "label":    "deepen the catcher",
        "cost":     {"scrap": 4},
        "desc":     "collects water every 3 actions instead of 4",
        "requires": "has_rain_catcher",
        "built": [
            "you extend the catch surface. more comes through in a shower.",
            "a wider basin, re-angled. the drip is more frequent now.",
        ],
    },
    {
        "key":      "extended_beacon",
        "label":    "extend the beacon",
        "cost":     {"scrap": 5},
        "desc":     "signal carries further",
        "requires": "has_signal_beacon",
        "built": [
            "you add length to the mast. the hum lifts.",
            "the signal reaches further now. something out there might notice.",
        ],
    },
    {
        "key":      "braced_connector",
        "label":    "brace the connector",
        "cost":     {"scrap": 3},
        "desc":     "connector wears more slowly",
        "requires": None,
        "built": [
            "you reinforce the fitting. it should hold longer.",
            "the connection feels more permanent now. less give.",
        ],
    },
    {
        "key":      "tending_frame",
        "label":    "tending frame",
        "cost":     {"scrap": 8, "power": 3},
        "desc":     "tends the garden while you are away",
        "requires": "has_garden_bed",
        "built": [
            "you assemble the frame from salvaged parts. it stands in the garden, waiting to be told what to do.",
            "upright in the beds. it doesn't do anything yet. you'll need to set it.",
        ],
    },
]

EXPLORE_PREP_INVEST = "you take a length of pipe. it has uses outside. (-1 scrap, +1 hp)"

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

# --- Flower Garden ------------------------------------------

FLOWER_ENTER = "you step into the flower garden."
FLOWER_LEAVE = "you leave the flower garden."
FLOWER_PLANT_OK       = "you press the {variety} into the soil."
FLOWER_PLANTED        = "you press the {flower} into the soil."
FLOWER_PLANT_OCCUPIED = "something is already growing here."
FLOWER_GARDEN_UNLOCKED = "{name} brought something with them. seeds, pressed flat in a cloth."

FLOWER_BLOOM_LINES = [
    "something has opened.",
    "colour, unexpected.",
    "a bloom. the bees will know before you do.",
    "quiet, and then — flowers.",
]

FLOWER_AMBIENT = [
    "the flower garden grows whether or not you tend it.",
    "the air here is slightly different. something to do with the blooms.",
    "a bee passes through. it does not stop, but it notices.",
    "the garden has its own schedule.",
    "something opened overnight. you weren't watching.",
    "the garden has its own sense of direction.",
    "the oldest flowers are the ones you didn't plant.",
]
