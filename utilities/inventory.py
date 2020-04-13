import time
import random

import cv2
import numpy as np

# Custom library
from tools.screen_pos import Pos, Box
from tools import config
from tools.lib import debug as console
from tools.lib import wait
from tools.lib import file_name
from data import regions

# Utilities
from utilities import ui

# Constants
ITEM_WIDTH = 32
ITEM_HEIGHT = 32
INVENTORY_BUFFER_HEIGHT = 2
INVENTORY_BUFFER_WIDTH = 8


def build_inventory_positions():
    positions = []
    for y in range(0, 7):
        for x in range(0, 4):
            tl = Pos(
                regions.INVENTORY_ITEM_FIRST_POS.x +
                    (x * ITEM_WIDTH) + (x * INVENTORY_BUFFER_WIDTH),
                regions.INVENTORY_ITEM_FIRST_POS.y +
                    (y * ITEM_HEIGHT) + (y * INVENTORY_BUFFER_HEIGHT)
            )
            positions.append(
                Box(tl, Pos(tl.x + ITEM_WIDTH, tl.y + ITEM_HEIGHT)))
    return positions


INVENTORY_POSITIONS = build_inventory_positions()


def check_inventory(client, items, return_first=False):
    # Open the inventory
    ui.open_inventory(client)

    time_start = time.time()

    # Force into an array
    if not isinstance(items, list):
        items = [items]

    found = {}
    for item in items:
        exit_early = False
        found[item.reference] = []
        for inv_pos in INVENTORY_POSITIONS:
            if exit_early:
                break
            if item.has_unique_threshold():
                client.set_threshold(item.threshold)
            find = client.find(item.reference, inv_pos)
            if find is not None:
                found[item.reference].append(find)
                if return_first:
                    exit_early = True

        console("Inventory - check_inventory: %s [%s]" %
                (file_name(item.reference), len(found[item.reference])))

    console("Inventory - check_inventory: check time = %s" %
            round(time.time() - time_start, 3))
    return found


def click_slot(client, slot):
    client.click(INVENTORY_POSITIONS[slot].random_point())


def has_amount(client, item, limit):
    found = check_inventory(client, item.reference)[item.reference]
    console("Inventory - has_amount: Found: %s" % len(found))
    return len(found) >= limit


def drop(client, item):
    item_positions = check_inventory(client, item.reference)[item.reference]
    for pos in item_positions:
        client.click(pos)
        wait(.3, .75)
