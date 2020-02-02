import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
import random
import sys

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
import bot
from tools import config
from tools import screen_search


BANK_BOOTH = [
    "bot_ref_imgs/banking/bank_booth.png",
    "bot_ref_imgs/banking/bank_booth_2.png"
]


BANK_WITHDRAW_X = Box(Pos(887, 989), Pos(932, 1028))


def bank_cycle(withdraw=[]):
    print(withdraw)
    # Open bank
    while not is_bank_open():
        open()
        time.sleep(random.randint(2, 5))
    
    # Bank inventory
    bank_inventory()
    time.sleep(random.randint(1, 3))

    # Withdraw items
    if isinstance(withdraw, list):
        for item in withdraw:
            withdraw_item(item)
    else:
        withdraw_item(withdraw)

    time.sleep(random.randint(1, 2))

    # Close
    close()


def is_select_x_inactive():
    check = screen_search.find_in_screen("bot_ref_imgs/banking/withdraw_x_inactive.png")
    return check is not None


def options_select_x():
    if is_select_x_inactive():
        bot.click(BANK_WITHDRAW_X.random_point())
        time.sleep(random.randint(1, 2))
        # Check if amount menu pops up
        check = screen_search.find_in_screen("bot_ref_imgs/banking/withdraw_x_amount.png")
        if check is not None:
            bot.type_string("14", True)



def bank_inventory():
    # Bank inventory
    click_pos = screen_search.find_in_screen("bot_ref_imgs/banking/bank_inventory.png")
    if click_pos is None:
        print("Couldn't find bank inventory icon, something is terribly wrong.")
        sys.exit()
    bot.click(click_pos)


def find_item(item_ref):
    return screen_search.find_in_screen(item_ref)


def withdraw_item(item_ref):
    print("Withdrawing: %s" % item_ref)
    click_pos = find_item(item_ref)
    if click_pos is None:
        print("Couldn't find item [%s]. Item is not in bank view.")
        return
    bot.click(click_pos)


def is_bank_open():
    check = screen_search.find_in_screen("bot_ref_imgs/banking/open_bank.png")
    return check is not None


def find_booth():
    booth_found = False
    for booth in BANK_BOOTH:
       check = screen_search.find_in_screen(booth)
       if check is not None:
           booth_found = True
           
    if not booth_found:
        print("Couldn't find bank booth... fuck.")
        return None
    
    return check
  

def close():
    click_pos = screen_search.find_in_screen("bot_ref_imgs/banking/close_bank.png")
    if click_pos is None:
        print("Couldn't close the bank. Something is terribly wrong.")
        sys.exit()
    bot.click(click_pos)


def open():
    booth = find_booth()
    if booth is None:
        sys.exit()
    bot.click(booth)