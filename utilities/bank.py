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

# Reference Images
BANK_BOOTH = [
    "bot_ref_imgs/quad_1080/bank/bank_booth_1.png",
    "bot_ref_imgs/quad_1080/bank/bank_booth_2.png",
    "bot_ref_imgs/quad_1080/bank/bank_booth_3.png",
    "bot_ref_imgs/quad_1080/bank/bank_booth_4.png"
]
WITHDRAW_X_INACTIVE = "bot_ref_imgs/quad_1080/bank/withdraw_x_inactive.png"
WITHDRAW_X_AMOUNT = "bot_ref_imgs/quad_1080/bank/withdraw_x_amount.png"
IS_BANK_OPEN = "bot_ref_imgs/quad_1080/bank/is_bank_open.png"


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


def options_select_x(session):
    if is_select_x_inactive(session):
        debug("BANK: Selecting 'withdraw x'")
        bot.click(session.translate(grabber.BANK_WITHDRAW_X.random_point()))
        wait(1, 2)
        # Check if amount menu pops up
        check = session.set_region_threshold(0.6).find_in_region(grabber.BANK, WITHDRAW_X_AMOUNT)
        if check is not None:
            bot.type_string("14", True)


def bank_inventory(session):
    if not is_bank_open(session):
        debug("BANK - bank_inventory: Bank wasn't open prior to calling this method. Exiting out, you fucked the script.")
        sys.exit()
    bot.click(session.translate(grabber.BANK_DEPOSIT_INVENTORY.random_point()))


def find_item(session, item_ref):
    return session.set_region_threshold(0.6).find_in_region(grabber.BANK, item_ref)


def withdraw_item(session, item_ref):
    debug("BANK - withdraw_item: %s" % file_name(item_ref))
    click_pos = find_item(session, item_ref)
    if click_pos is None:
        debug("BANK - withdraw_item: Couldn't find item [%s]. Item is not in bank view." % file_name(item_ref))
        return
    # Already translated due to find_in_region
    bot.click(click_pos)


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
        bot.click(session.translate(grabber.BANK_CLOSE.random_point()))


def open(session):
    booth = find_booth(session)
    if booth is None:
        debug("BANK - open: Couldn't open the bank. Script is exiting because you're not in a bank.")
        sys.exit()
    bot.click(booth)