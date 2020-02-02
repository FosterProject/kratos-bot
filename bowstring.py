import time
import random
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2

# Custom Library
import tools.image_lib as imlib
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos, Box
from tools import config
import bot

# OSRS Specific
import inventory
import movement
import bank
import ui
import account


# Globals
LOGIN_TIME = 0
LOGIN_TIMER_CAP = 0
TRUE_NORTH_TIME = 0
TRUE_NORTH_TIMER_CAP = 0


# Timers
LOGIN_TIMER_CAP_MIN = 20 * 60
LOGIN_TIMER_CAP_MAX = 300 * 60

LOGOUT_TIME_MIN = 5
LOGOUT_TIME_MAX = 40

TRUE_NORTH_TIMER_MIN = 10
TRUE_NORTH_TIMER_MAX = 30

STRINGING_TIME = 20
STRING_TIME_ERROR = 5


# Images
BOW_STRUNG_REFERENCE = "bot_ref_imgs/fletching/maple_longbow.png"
BOW_UNSTRUNG_REFERENCE = "bot_ref_imgs/fletching/maple_longbow_u.png"
STRING_REFERENCE = "bot_ref_imgs/fletching/bowstring.png"


# Positions
# STRING_ALL = Box(Pos(), Pos())


def wait(min, max):
    time.sleep(random.randint(min, max))


def startup():
    # Log in
    account.login()
    time.sleep(random.randint(3, 6))

    # True North
    ui.click_compass()

    # Check if at the bank
    at_bank_check = bank.find_booth()
    if at_bank_check is None:
        print("Please start the bot at Varrock East bank")
        sys.exit()

    # Open inventory
    ui.open_inventory()

    # Open bank and empty inventory
    while not bank.is_bank_open():
        bank.open()
        time.sleep(random.randint(2, 5))
    bank.bank_inventory()

    # Toggle select x
    bank.options_select_x()


def finished_stringing():
    return inventory.has_amount(BOW_STRUNG_REFERENCE, 14)


def withdraw_resources():
    bank.withdraw_item(BOW_UNSTRUNG_REFERENCE)
    wait(1, 3)
    bank.withdraw_item(STRING_REFERENCE)
    wait(1, 3)


def set_login_timers():
    global LOGIN_TIME
    global LOGIN_TIMER_CAP
    LOGIN_TIME = time.time()
    LOGIN_TIMER_CAP = random.randint(LOGIN_TIMER_CAP_MIN, LOGIN_TIMER_CAP_MAX)


def set_true_north_timers():
    global TRUE_NORTH_TIME
    global TRUE_NORTH_TIMER_CAP
    TRUE_NORTH_TIME = time.time()
    TRUE_NORTH_TIMER_CAP = random.randint(TRUE_NORTH_TIMER_MIN, TRUE_NORTH_TIMER_MAX)


def start_stringing():
    bow = inventory.find(BOW_UNSTRUNG_REFERENCE)
    if bow is None:
        print("Couldn't find bow, bot is FUCKED.")
        sys.exit()
    string = inventory.find(STRING_REFERENCE)
    if string is None:
        print("Couldn't find bowstring, bot is FECKED.")
        sys.exit()
    
    bot.click(bow)
    wait(2, 3)
    bot.click(string)


if __name__ == "__main__":
    # Startup
    startup()

    # Set login timer
    set_login_timers()

    # Start fletching loop
    while True:
        # Check if true north needs to be clicked
        if time.time() - TRUE_NORTH_TIME >= TRUE_NORTH_TIMER_CAP:
            ui.click_compass()
            set_true_north_timers()

        # Withdraw bows and strings
        withdraw_resources()

        # Close bank
        bank.close()
        wait(2, 4)

        # Click on a bow and click on a string
        start_stringing()
        wait(2, 4)

        # Click fletch all or send a space key
        bot.press_space()

        # Wait until 14 objects (strung bows if possible) in inventory
        # while not finished_stringing():
        #     wait(2, 4)
        wait(STRINGING_TIME, STRINGING_TIME + STRING_TIME_ERROR)

        # Open bank and bank inventory
        while not bank.is_bank_open():
            bank.open()
            time.sleep(random.randint(2, 5))
        bank.bank_inventory()
        wait(2, 3)

        # if current run time exceeds cap
        if time.time() - LOGIN_TIME >= LOGIN_TIMER_CAP:
            # Reset timer values
            set_login_timers()

            # Logout
            account.logout()

            # Sleep for random value
            wait(LOGOUT_TIME_MIN, LOGOUT_TIME_MIN)

            # Call startup routine
            startup()
            