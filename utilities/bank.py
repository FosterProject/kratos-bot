import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import random
import sys

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import bot
from tools import config
from tools import screen_search
from tools.lib import wait
from tools.lib import debug
from tools.lib import file_name
from tools.event_manager import Event

# Reference Images
BANK_BOOTH = [
    # "bot_ref_imgs/bank/bank_booth_1.png",
    # "bot_ref_imgs/bank/bank_booth_2.png",
    # "bot_ref_imgs/bank/bank_booth_3.png",
    # "bot_ref_imgs/bank/bank_booth_4.png",
    "bot_ref_imgs/bank/bank_booth_5.png"
]
WITHDRAW_ALL_INACTIVE = "bot_ref_imgs/bank/withdraw_all_inactive.png"
WITHDRAW_X_INACTIVE = "bot_ref_imgs/bank/withdraw_x_inactive.png"
WITHDRAW_X_AMOUNT = "bot_ref_imgs/bank/withdraw_x_amount.png"
IS_BANK_OPEN = "bot_ref_imgs/bank/is_bank_open.png"


def bank_cycle(session, withdraw=[]):
    # Open bank
    while not is_bank_open(session):
        open(session)
        wait(2, 5)
    
    # Bank inventory
    bank_inventory(session)
    wait(1, 3)

    # Withdraw items
    if isinstance(withdraw, list):
        for item in withdraw:
            withdraw_item(session, item)
    else:
        withdraw_item(session, withdraw)

    wait(1, 2)

    # Close
    close(session)


def is_select_x_inactive(session):
    check = session.find_in_region(grabber.BANK, WITHDRAW_X_INACTIVE)
    return check is not None


def is_select_all_inactive(session):
    check = session.find_in_region(grabber.BANK, WITHDRAW_ALL_INACTIVE)
    return check is not None


def options_select_all(session):
    if is_select_all_inactive(session):
        debug("BANK: Selecting 'withdraw all'")

        # Click withdraw all
        event = Event([
            (Event.click(session.translate(grabber.BANK_WITHDRAW_ALL.random_point())), (.5, 1))
        ])

        session.publish_event(event)


def options_select_x(session):
    if is_select_x_inactive(session):
        debug("BANK: Selecting 'withdraw x'")

        # Click withdraw x
        event = Event([
            (Event.click(session.translate(grabber.BANK_WITHDRAW_X.random_point())), (1, 2))
        ])

        # Check if amount menu pops up
        check = session.find_in_client(WITHDRAW_X_AMOUNT)
        if check is not None:
            event.add_action(Event.type_string("14", True), (.5, 1))

        session.publish_event(event)


def bank_inventory(session):
    return session.translate(grabber.BANK_DEPOSIT_INVENTORY.random_point())


def find_item(session, item):
    if item.has_unique_threshold():
        session.set_region_threshold(item.threshold)
    return session.find_in_region(grabber.BANK, item.reference)


def withdraw_item(session, item):
    debug("BANK - withdraw_item: %s" % file_name(item.reference))
    click_pos = find_item(session, item)
    if click_pos is None:
        debug("BANK - withdraw_item: Couldn't find item [%s]. Item is not in bank view." % file_name(item.reference))
        return
    # Already translated due to find_in_region
    return click_pos


def is_bank_open(session):
    check = session.find_in_region(grabber.BANK, IS_BANK_OPEN)
    return check is not None


def find_booth(session):
    booth_found = False
    for booth in BANK_BOOTH:
       check = session.find_in_client(booth)
       if check is not None:
           booth_found = True
           break
           
    if not booth_found:
        debug("BANK - find_booth: Couldn't find bank booth in client")
        return None
    
    return check
  

def close(session):
    debug("BANK - close: Closing the bank")
    if is_bank_open(session):
        return session.translate(grabber.BANK_CLOSE.random_point())
    return None


def open(session):
    booth_pos = find_booth(session)
    if booth_pos is None:
        debug("BANK - open: Couldn't open the bank. Script is exiting because you're not in a bank.")
        sys.exit()
    return booth_pos