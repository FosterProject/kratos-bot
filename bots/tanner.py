import sys
import time
import random

# Base session
from tools.session import Session

# Libraries
from tools import bot
from tools.lib import wait
from tools.lib import debug
from tools.lib import error
from tools.event_manager import EventManager, Event

# Utilities
from utilities import account
from utilities import ui
from utilities import bank
from utilities import inventory
from utilities.items import Item

# Image References
UNTANNED_HIDE = "bot_ref_imgs/tanner/cowhide.png"
TANNED_HIDE = "bot_ref_imgs/tanner/hard_leather.png"
CASH_STACK_BANK = "bot_ref_imgs/tanner/cash_stack_bank.png"

# Constants


class Tanner:
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

    
    # Bot startup actions
    def startup(self):
        debug("Kratos-Bot >> Running Tanner startup...")
        # Login
        account.login(self.session)
        wait(2, 3)

        # True north
        compass_pos = ui.click_compass(self.session)
        self.session.publish_event(Event([
            (Event.click(compass_pos), (.2, .4))
        ]))

        # At bank check
        if bank.find_booth(self.session) is None:
            print("Kratos-Bot >> Please start this bot in Al Kharid bank")
            sys.exit()

        # Open bank and empty inventory
        self.bank_inventory()

        # Withdraw cash stack
        self.withdraw_cash_stack()

        # Toggle select x
        bank.options_select_all(self.session)

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

            # Start an event list
            event = Event()

            # Withdraw untanned hides
            self.withdraw_resources(event)

            # Close the bank
            bank_close_pos = bank.close(self.session)
            if bank_close_pos is None:
                error("bot has fallen out of sync, it thinks the bank is open and when it isn't")
                return
            event.add_action(Event.click(bank_close_pos), (.8, 1.3))

            # Publish this current event and wait for processing
            self.session.publish_event(event)


            # Move to tanner
            self.start_stringing_action(event)

            # Find tanner and tan hides

            # Move to bank

            # Bank inventory
            self.bank_inventory()

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
        event = Event()

        # Open bank
        if not bank.is_bank_open(self.session):
            booth_pos = bank.open(self.session)
            event.add_action(Event.click(booth_pos), (1.5, 2.5))

        # Empty inventory
        bank_inventory_pos = bank.bank_inventory(self.session)
        event.add_action(Event.click(bank_inventory_pos), (.5, 1))

        # Publish actions
        self.session.publish_event(event)


    def withdraw_cash_stack(self):
        # TODO: Implement this function
        pass


    def withdraw_resources(self, event):
        res1_pos = bank.withdraw_item(self.session, UNTANNED_HIDE)
        event.add_action(Event.click(res1_pos), (.5, 1))


    def true_north(self):
        if time.time() - self._true_north_timer >= self._true_north_timer_cap:
            # Reset timers
            self._true_north_timer_cap = random.randint(8, 25)
            self._true_north_timer = time.time()

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([
                (Event.click(compass_pos))
            ]))
