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
BOWSTRING = Item("bot_ref_imgs/fletching/bowstring.png", 0.32)
BOWSTRING_SHORT = Item("bot_ref_imgs/fletching/bowstring_short.png", 0.32)
UNSTRUNG = Item("bot_ref_imgs/fletching/yew_unstrung.png", 0.33)
UNSTRUNG_SHORT = Item("bot_ref_imgs/fletching/yew_unstrung_short.png", 0.33)
LONGBOW = Item("bot_ref_imgs/fletching/yew_longbow.png")

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
        debug("Kratos-Bot >> Running Bowstringer startup...")
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
            print("Kratos-Bot >> Please start this bot at a south-facing bank")
            sys.exit()
        
        # Open inventory
        open_inventory_pos = ui.open_inventory(self.session)
        if open_inventory_pos is not None:
            self.session.publish_event(Event([
                (Event.click(open_inventory_pos), (.5, 1))
            ]))

        # Open bank and empty inventory
        self.bank_inventory()

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
            run_timer = time.time()

            if self.session.should_exit():
                print("EXITING BOT LOOP")
                break

            # Start an event list
            event = Event()

            # Withdraw bows and strings
            self.withdraw_resources(event)

            # Close the bank
            bank_close_pos = bank.close(self.session)
            if bank_close_pos is None:
                error("bot has fallen out of sync, it thinks the bank is open and when it isn't")
                return
            event.add_action(Event.click(bank_close_pos), (.8, 1.3))

            # Start stringing action
            self.start_stringing_action(event)

            # Confirm stringing
            self.confirm_stringing(event)

            # Kick off all those actions
            self.session.publish_event(event)

            # Wait for minimum stringing time in case the event gets processed immediately
            wait(STRINGING_TIME, STRINGING_TIME + self._stringing_time_error)

            # Check if need to click true north
            self.true_north()

            # Bank inventory
            self.bank_inventory()

            print(" --- RUN TIMER: [%s] --- " % (round((time.time() - run_timer)) / 60, 2))

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


    def start_stringing_action(self, event):
        # Click on inventory tile between 0 - 13
        pos1 = inventory.click_slot(self.session, random.randint(0, 13))
        pos2 = inventory.click_slot(self.session, random.randint(14, 27))
        event.add_action(Event.click(pos1), (.8, 1.2))
        event.add_action(Event.click(pos2), (1.5, 2.5))


    def confirm_stringing(self, event):
        event.add_action(Event.press_space())


    def withdraw_resources(self, event):
        unstrung_pos = bank.withdraw_item(self.session, UNSTRUNG_SHORT)
        bowstring_pos = bank.withdraw_item(self.session, BOWSTRING_SHORT)
        event.add_action(Event.click(unstrung_pos), (.5, 1))
        event.add_action(Event.click(bowstring_pos), (.5, 1))


    def true_north(self):
        if time.time() - self._true_north_timer >= self._true_north_timer_cap:
            # Reset timers
            self._true_north_timer_cap = random.randint(8, 25)
            self._true_north_timer = time.time()

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([
                (Event.click(compass_pos), (.4, .8))
            ]))
