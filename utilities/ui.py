import random
import sys

# Custom library
from tools import osrs_screen_grab as grabber
from tools.screen_pos import Pos
from tools import bot
from tools import config
from tools import screen_search
from tools.lib import debug
from tools.lib import wait


# DURATIONS
DRAG_DURATION_MIN = 0.4
DRAG_DURATION_MAX = 0.7

# Constants
BAR_TAB_HEIGHT = 38

# Images
INVENTORY_ICON_ACTIVE = "bot_ref_imgs/ui/inv_icon_active.png"
INVENTORY_FULL = "bot_ref_imgs/ui/inventory_full.png"

RUN_FULL = "bot_ref_imgs/ui/full_run.png"


def open_tab(session, side, item):
    if side != "LEFT" and side != "RIGHT":
        debug("UI: side value not LEFT or RIGHT")
        sys.exit()
    bar = grabber.BAR_LEFT_TOP if side == "LEFT" else grabber.BAR_RIGHT_TOP

    tab_bounds = bar.copy()
    tab_bounds.shift_y(item * BAR_TAB_HEIGHT)

    return session.translate(tab_bounds.random_point())


def click_tap_option(session):
    return session.translate(grabber.TAP_OPTION.random_point())


def inventory_full(session):
    return session.find_in_client(INVENTORY_FULL) is not None


def run_full(session):
    return session.find_in_client(RUN_FULL) is not None


def is_inventory_open(session):
    check = session.find_in_client(INVENTORY_ICON_ACTIVE)
    return check is not None


def open_inventory(session):
    debug("UI: Opening inventory")
    while not is_inventory_open(session):
        return open_tab(session, "RIGHT", 0)


def click_compass(session):
    return session.translate(grabber.COMPASS.random_point())


def spin_around(session):
    y_bound = 25
    x_error = int(config.GAME_WIDTH / 10)
    y_error = 50

    x_start = random.randint(
        grabber.DRAG_BOUNDS.tl.x,
        grabber.DRAG_BOUNDS.tl.x + random.randint(x_error, x_error * 2)
    )
    y_start = random.randint(
        grabber.DRAG_BOUNDS.tl.y,
        grabber.DRAG_BOUNDS.br.y + random.randint(5, y_error)
    )
    x_end = random.randint(
        int((grabber.DRAG_BOUNDS.br.x * 0.85)) - random.randint(x_error, x_error * 2),
        int(grabber.DRAG_BOUNDS.br.x * 0.85)
    )
    y_end = random.randint(
        y_start,
        y_start + y_bound
    )

    start = session.translate(Pos(x_start, y_start))
    end = session.translate(Pos(x_end, y_end))

    return (start, end, round(random.uniform(DRAG_DURATION_MIN, DRAG_DURATION_MAX), 2))