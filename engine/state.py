# engine/state.py
# Game state — single source of truth. Save/load via JSON.

import json
import os
import time
import random
from dataclasses import dataclass, field
from typing import Optional

SAVE_DIR  = os.path.expanduser("~/.quietcurrent")
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")
VERSION   = "0.2.0"

GARDEN_W = 12
GARDEN_H = 8
GARDEN_SIZE = GARDEN_W * GARDEN_H

RESIDENT_MAX = 8


@dataclass
class PlotState:
    state:    str   = "E"    # E D P G R W X
    soil:     int   = 1      # 1-5
    moisture: int   = 0      # 0-5
    crop:     str   = "none"
    growth:   int   = 0      # 0-100


@dataclass
class Resident:
    name:  str
    mood:  int = 2    # 3=thriving 2=stable 1=uneasy 0=departing
    days:  int = 0


@dataclass
class GameState:
    # Identity
    settlement_name:     str   = "unnamed"
    version:             str   = VERSION

    # Panel
    panel_state:         str   = "neglected"   # neglected cleaned connected
    panel_efficiency:    int   = 100
    panel_dust:          bool  = False
    panel_wire:          bool  = False
    panel_debris:        bool  = False
    panel_connector:     bool  = False

    # Resources
    power:  int = 0
    scrap:  int = 0
    water:  int = 0
    seeds:  int = 0

    # Progress counters
    tend_count:          int   = 0
    gather_count:        int   = 0
    action_count:        int   = 0
    ancestral_revealed:  int   = 0
    days_founded:        int   = 0

    # Buildings (flags)
    has_junction_box:    bool  = False
    has_rain_catcher:    bool  = False
    has_garden_bed:      bool  = False
    has_signal_beacon:   bool  = False
    has_compost_pile:    bool  = False
    compost_level:       int   = 0    # 0-5

    # Weather
    weather:             str   = "sunny"
    weather_duration:    int   = 0

    # Wanderer
    wanderer_count:      int   = 0

    # Residents
    residents: list = field(default_factory=list)   # list of Resident dicts

    # Garden
    garden_initialized:  bool  = False
    garden:              list  = field(default_factory=list)   # GARDEN_SIZE PlotState dicts

    # Timestamps
    last_seen:           float = field(default_factory=time.time)

    def resident_count(self) -> int:
        return len(self.residents)

    def active_garden_plots(self) -> int:
        return sum(
            1 for p in self.garden
            if p.get("state") in ("G", "R")
        )

    def weedy_plots(self) -> int:
        return sum(1 for p in self.garden if p.get("state") == "W")


# ── Serialization ────────────────────────────────────────────

def _state_to_dict(gs: GameState) -> dict:
    d = {k: v for k, v in gs.__dict__.items()}
    return d


def _dict_to_state(d: dict) -> GameState:
    gs = GameState()
    for k, v in d.items():
        if hasattr(gs, k):
            setattr(gs, k, v)
    return gs


# ── Save / Load ──────────────────────────────────────────────

def save_game(gs: GameState) -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    gs.last_seen = time.time()
    with open(SAVE_FILE, "w") as f:
        json.dump(_state_to_dict(gs), f, indent=2)


def load_game() -> Optional[GameState]:
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE) as f:
            d = json.load(f)
        gs = _dict_to_state(d)
        # Migrate old saves — fill missing fields with defaults
        default = GameState()
        for k, v in default.__dict__.items():
            if not hasattr(gs, k) or getattr(gs, k) is None:
                setattr(gs, k, v)
        return gs
    except (json.JSONDecodeError, KeyError):
        return None


def delete_save() -> None:
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


# ── Time ─────────────────────────────────────────────────────

def days_since_last_seen(gs: GameState) -> int:
    elapsed = time.time() - gs.last_seen
    return int(elapsed // 86400)


# ── Garden helpers ───────────────────────────────────────────

def init_garden() -> list:
    plots = []
    for _ in range(GARDEN_SIZE):
        plots.append({
            "state":    "E",
            "soil":     random.randint(1, 2),
            "moisture": 0,
            "crop":     "none",
            "growth":   0,
        })
    return plots


def plot_idx(x: int, y: int) -> int:
    return y * GARDEN_W + x
