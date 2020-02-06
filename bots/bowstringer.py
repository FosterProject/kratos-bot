import sys
import time
import random

# Base session
from tools.session import Session

# Libraries
from tools import bot
from tools.lib import wait
from tools.lib import debug

# Utilities
from utilities import account
from utilities import ui
from utilities import bank
from utilities import inventory
from utilities.items import Item

# Image References
BOWSTRING = Item("bot_ref_imgs/quad_1080/fletching/bowstring.png", 0.32)
BOWSTRING_SHORT = Item("bot_ref_imgs/quad_1080/fletching/bowstring_short.png", 0.32)
UNSTRUNG = Item("bot_ref_imgs/quad_1080/fletching/yew_unstrung.png", 0.33)
UNSTRUNG_SHORT = Item("bot_ref_imgs/quad_1080/fletching/yew_unstrung_short.png", 0.33)
LONGBOW = Item("bot_ref_imgs/quad_1080/fletching/yew_longbow.png")

# Constants
STRINGING_TIME = 18

class Bowstringer:
    def __init__(self, session):
        self.session = session

        # Login timers
        self.min_login_time = 15 * 60
        self.max_login_time = 280 * 60
        self.min_logout_time = 5 * 60
        self.max_logout_time = 50 * 60

        # UI Timers
        self._true_north_timer = time.time()
        self._true_north_timer_cap = 14 * 60

        # Randomness variables
        self._stringing_time_error = 5

    
    # Bot startup actions
    def startup(self):
        debug("Kratos-Bot >> Running bot startup...")
        # Login
        account.login(self.session)
        wait(2, 3)

        # True north
        ui.click_compass(self.session)
        wait(.5, 1)

        # At bank check
        if bank.find_booth(self.session) is None:
            print("Kratos-Bot >> Please start this bot at a south-facing bank")
            sys.exit()
        
        # Open inventory
        ui.open_inventory(self.session)
        wait(.5, 1)

        self.bank_inventory()
        wait(.3, .8)

        # Toggle select x
        bank.options_select_x(self.session)

        # Setup login timers
        self.session.set_login_time_max(self.min_login_time, self.max_login_time)


    # Run bot
    def run(self):
        debug("Kratos-Bot >> Running startup routine")
        self.startup()

        debug("Kratos-Bot >> Starting main bot loop")

        while True:
            if self.session.should_exit():
                print("EXITING BOT LOOP")
                break

            # Check if need to click true north
            self.true_north()

            # Withdraw bows and strings
            self.withdraw_resources()

            # Close the bank
            bank.close(self.session)
            wait(1, 2)

            # Start stringing action
            self.start_stringing_action()

            # Confirm stringing
            self.confirm_stringing()

            # Wait for stringing
            wait(STRINGING_TIME, STRINGING_TIME + self._stringing_time_error)

            # Bank inventory
            self.bank_inventory()
            wait(.5, 1)

            # Check if we need to log out
            if self.session.should_log_out():
                # Reset login timers
                self.session.set_login_time_max(self.min_login_time, self.max_login_time)
                self.session.reset_login_time()

                # Logout
                account.logout(self.session)

                # Sleep for logout time
                wait(self.min_logout_time, self.max_logout_time)

                # Startup
                self.startup()


    def bank_inventory(self):
        # Empty inventory
        while not bank.is_bank_open(self.session):
            bank.open(self.session)
            wait(1, 2)
        bank.bank_inventory(self.session)


    def start_stringing_action(self):
        # Click on inventory tile between 0 - 13
        inventory.click_slot(self.session, random.randint(0, 13))
        wait(.5, 1.2)
        inventory.click_slot(self.session, random.randint(14, 27))
        wait(.5, 1.2)


    def confirm_stringing(self):
        bot.press_space()


    def withdraw_resources(self):
        bank.withdraw_item(self.session, UNSTRUNG_SHORT)
        wait(1, 2)
        bank.withdraw_item(self.session, BOWSTRING_SHORT)
        wait(1, 2)


    def true_north(self):
        if time.time() - self._true_north_timer >= self._true_north_timer_cap:
            ui.click_compass(self.session)
            self._true_north_timer_cap = random.randint(8, 25)
            self._true_north_timer = time.time()


