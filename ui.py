import random

# Custom library
from tools.screen_pos import Pos
import bot
from tools import config
from tools import screen_search


# BOUNDS
COMPASS = {
    "TL": Pos(1517, 18),
    "BR": Pos(1576, 73)
}

INVENTORY = {
    "TL": Pos(1816, 442),
    "BR": Pos(1880, 506)
}

DRAG_BOUNDS = {
    "TL": Pos(382, 248),
    "BR": Pos(1618, 906)
}

# DURATIONS
DRAG_DURATION_MIN = 0.4
DRAG_DURATION_MAX = 1.3


def is_inventory_open():
    check = screen_search.find_in_screen("bot_ref_imgs/ui/inv_icon_active.png")
    if check is None:
        return False, Pos.random(INVENTORY["TL"], INVENTORY["BR"])
    return True, None


def open_inventory():
    success, click_pos = is_inventory_open()
    if success is True:
        print("Inventory is already open you cock")
    else:
        bot.click(click_pos)


def click_compass():
    bot.click(Pos.random(COMPASS["TL"], COMPASS["BR"]))


def spin_around():
    y_bound = 25
    x_error = 25
    y_error = 50

    x_start = random.randint(
        DRAG_BOUNDS["TL"].x,
        DRAG_BOUNDS["TL"].x + random.randint(5, x_error)
    )
    y_start = random.randint(
        DRAG_BOUNDS["TL"].y,
        DRAG_BOUNDS["BR"].y + random.randint(5, y_error)
    )
    x_end = random.randint(
        int((DRAG_BOUNDS["BR"].x * 0.85)) - random.randint(5, x_error),
        int(DRAG_BOUNDS["BR"].x * 0.85)
    )
    y_end = random.randint(
        y_start,
        y_start + y_bound
    )

    # Reverse direction half the time
    start = Pos(x_start, y_start)
    end = Pos(x_end, y_end)
    # if random.randint(1, 2) == 2:
    #     x = start
    #     start = end
        # end = x
    bot.drag(start, end, round(random.uniform(DRAG_DURATION_MIN, DRAG_DURATION_MAX), 2))
