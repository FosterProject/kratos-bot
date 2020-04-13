import random
import sys

import win32con

# Custom library
from tools.screen_pos import Pos
from tools import config
from tools.lib import debug as console
from tools.lib import wait
from data import regions


# DURATIONS
DRAG_DURATION_MIN = 0.4
DRAG_DURATION_MAX = 0.7

# Constants
BAR_TAB_HEIGHT = 38

# Images
INVENTORY_ICON_ACTIVE = "bot_ref_imgs/ui/inv_icon_active.png"
INVENTORY_FULL = "bot_ref_imgs/ui/inventory_full.png"

RUN_FULL = "bot_ref_imgs/ui/full_run.png"


def open_tab(client, side, item):
    if side != "LEFT" and side != "RIGHT":
        console("UI: side value not LEFT or RIGHT")
        sys.exit()
    bar = regions.BAR_LEFT_TOP if side == "LEFT" else regions.BAR_RIGHT_TOP

    tab_bounds = bar.copy()
    tab_bounds.shift_y(item * BAR_TAB_HEIGHT)

    client.click(tab_bounds.random_point())


def click_tap_option(client):
    client.click(regions.TAP_OPTION.random_point())


def inventory_full(client):
    return client.find(INVENTORY_FULL) is not None


def run_full(client):
    return client.set_threshold(.8).find(RUN_FULL) is not None


def is_inventory_open(client):
    check = client.set_threshold(.8).find(INVENTORY_ICON_ACTIVE)
    return check is not None


def open_inventory(client):
    console("UI: Opening inventory")
    while not is_inventory_open(client):
        open_tab(client, "RIGHT", 0)
        wait(.1, .15)


def click_compass(client):
    client.click(regions.COMPASS.random_point())


def spin_around(client):
    client.key(win32con.VK_END)