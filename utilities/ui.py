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
SETTINGS_ICON_ACTIVE = "bot_ref_imgs/ui/settings_icon_active.png"
SETTINGS_RESTORE_DEFAULT_ZOOM = "bot_ref_imgs/ui/restore_default_zoom.png"

RUN_FULL = "bot_ref_imgs/ui/full_run.png"
TAP_OPTION_ON = "bot_ref_imgs/ui/tap_option_on.png"


def open_tab(client, side, item):
    if side != "LEFT" and side != "RIGHT":
        console("UI: side value not LEFT or RIGHT")
        sys.exit()
    bar = regions.BAR_LEFT_TOP if side == "LEFT" else regions.BAR_RIGHT_TOP

    tab_bounds = bar.copy()
    tab_bounds.shift_y(item * BAR_TAB_HEIGHT)

    client.click(tab_bounds.random_point())


def click_tap_option(client, on):
    check = client.set_threshold(.9999).find(TAP_OPTION_ON, regions.TAP_OPTION)
    if on:
        while check == None:
            client.click(regions.TAP_OPTION.random_point())
            wait(.8, .9)
            check = client.set_threshold(.9999).find(TAP_OPTION_ON, regions.TAP_OPTION)
    else:
        while check != None:
            client.click(regions.TAP_OPTION.random_point())
            wait(.8, .9)
            check = client.set_threshold(.9999).find(TAP_OPTION_ON, regions.TAP_OPTION)
            




def inventory_full(client):
    return client.find(INVENTORY_FULL) is not None


def click_run_orb(client):
    client.click(regions.RUN_ORB.random_point())


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


def lock_zoom(client):
    # Is settings open
    settings_open = client.set_threshold(.8).find(SETTINGS_ICON_ACTIVE)
    if not settings_open:
        client.key(win32con.VK_F10)
        wait(.1, .15)
    
    # Reset zoom level
    click_tap_option(client, True)
    wait(.2, .4)
    client.click(regions.ZOOM_CONTROL.random_point())
    wait(.2, .4)
    rdz_pos = client.find(SETTINGS_RESTORE_DEFAULT_ZOOM)
    if rdz_pos is None:
        print("Fucked up")
        return
    client.click(rdz_pos)
    wait(.2, .4)
    click_tap_option(client, False)
    wait(.2, .4)

    # Lock zoom camera
    client.click(regions.ZOOM_CONTROL.random_point())
    wait(.2, .4)
    
    # Close settings again
    client.key(win32con.VK_F10)


def spin_around(client):
    client.key(win32con.VK_END)