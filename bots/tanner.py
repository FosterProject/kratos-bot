# Base imports
import sys
import time
import random

# Darkflow
import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import cv2
import numpy as np

# Libraries
from tools import osrs_screen_grab as grabber
from tools import image_lib as imlib
from tools import bot
from tools.lib import wait
from tools.lib import debug
from tools.lib import error
from tools.lib import translate_predictions
from tools.event_manager import Event
from tools.screen_pos import Box, Pos

# Utilities
from utilities import account
from utilities import ui
from utilities import bank
from utilities import inventory
from utilities.items import Item
from utilities.movement import Movement


# Image References
UNTANNED_HIDE = Item("bot_ref_imgs/tanner/cowhide_short.png", .3)
TANNED_HIDE = Item("bot_ref_imgs/tanner/hard_leather.png", .3)
CASH_STACK_BANK = Item("bot_ref_imgs/tanner/cash_stack_bank.png", .3)

UNTANNED_HIDE_EMPTY = "bot_ref_imgs/tanner/cowhide_empty.png"

TRADE_WITH_TANNER = "bot_ref_imgs/tanner/trade_ellis.png"
TAN_ALL = "bot_ref_imgs/tanner/tan_all_smaller.png"
TANNER_OPEN = "bot_ref_imgs/tanner/tanner_open.png"

# Movement Images
MOVEMENT_TANNER_PATH = [
    "bot_ref_imgs/tanner/movement/1.png",
    "bot_ref_imgs/tanner/movement/2.png"
]
MOVEMENT_BANK_PATH = [
    "bot_ref_imgs/tanner/movement/1.png",
    "bot_ref_imgs/tanner/movement/0.png"   
]

# Positions (Unique to bot so not in grabber)
TANNING_INTERFACE = Box(Pos(124, 163), Pos(585, 447))
TAN_SOFT_LEATHER = Box(Pos(183, 227), Pos(215, 255))


# Load Darkflow
TFNET_OPTIONS = {
    "pbLoad": "brain_tanner/yolo-kratos.pb",
    "metaLoad": "brain_tanner/yolo-kratos.meta",
    "labels": "./labels.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)


class Tanner:
    def __init__(self, session, target_leather):
        self.session = session
        self.target_leather = target_leather

        # Movement
        self.tanner_route = Movement(session, MOVEMENT_TANNER_PATH)
        self.bank_route = Movement(session, MOVEMENT_BANK_PATH)

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
            (Event.click(compass_pos), None)
        ]))

        # At bank check
        if bank.find_booth(self.session, "EAST") is None:
            print("Kratos-Bot >> Please start this bot in Al Kharid bank")
            sys.exit()

        # Open bank and empty inventory
        self.bank_inventory()

        # Toggle select all
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

            # Withdraw untanned hides
            self.withdraw_resources()
            wait(1.1, 1.7)

            # Logout if out of resources
            out_of_resource = self.session.find_in_region(grabber.BANK, UNTANNED_HIDE_EMPTY) is not None

            # Close the bank
            bank_close_pos = bank.close(self.session)
            if bank_close_pos is None:
                error("bot has fallen out of sync, it thinks the bank is open and when it isn't")
                break
            event = Event()
            event.add_action(Event.click(bank_close_pos), (.3, .6) if out_of_resource else None)
            if out_of_resource:
                event.add_action(Event.click(bank_close_pos))
            self.session.publish_event(event)

            # Log out checkpoint
            if out_of_resource:
                account.logout(self.session)
                self.session.exit()
                break

            
            # Full run
            if ui.run_full(self.session):
                self.session.publish_event(Event([
                    (Event.click(self.session.translate(grabber.RUN_ORB.random_point())), None)
                ]))

            # Move to tanner
            self.move(self.tanner_route)

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([
                (Event.click(ui.click_compass(self.session)), None)
            ]))

            # Find tanner and tan hides
            self.tan_hides()

            # Disable two-step click
            self.session.publish_event(Event([
                (Event.click(ui.click_compass(self.session)), None)
            ]))

            # Move to bank
            self.move(self.bank_route)

            # Bank inventory
            self.bank_inventory()
            wait(.8, 1.3)

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


    def move(self, route):
        while not route.finished:
            step_pos = route.step()
            self.session.publish_event(Event([
                (Event.click(step_pos), None)
            ]))
            while route.is_moving:
                route.check_is_moving()
                wait(.2, .5)
        route.reset()


    def bank_inventory(self):
        # Open bank
        if not bank.is_bank_open(self.session):
            booth_pos = bank.open(self.session, "EAST")
            self.session.publish_event(Event([
                (Event.click(booth_pos), None)
            ]))
            wait(1.5, 2.5)

        idle_time = time.time()
        while not bank.is_bank_open(self.session):
            if time.time() - idle_time >= 6:
                self.session.publish_event(Event([
                    (Event.click(ui.click_compass(self.session)), None)
                ]))
                booth_pos = bank.open(self.session, "EAST")
                self.session.publish_event(Event([
                    (Event.click(booth_pos), None)
                ]))
                wait(1.5, 2.5)
                idle_time = time.time()
            else:
                print("Waiting to open the bank")
                wait(.5, 1)

        # Empty inventory
        bank_inventory_pos = bank.bank_inventory(self.session)
        self.session.publish_event(Event([
            (Event.click(bank_inventory_pos), None)
        ]))


    def withdraw_resources(self):
        res1_pos = bank.withdraw_item(self.session, UNTANNED_HIDE)
        self.session.publish_event(Event([
            (Event.click(res1_pos), None)
        ]))


    def true_north(self):
        if time.time() - self._true_north_timer >= self._true_north_timer_cap:
            # Reset timers
            self._true_north_timer_cap = random.randint(8, 25)
            self._true_north_timer = time.time()

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([
                (Event.click(compass_pos), (.1, .3))
            ]))


    def tan_hides(self):
        def click_on_tanner():
            # Click on trade with tanner
            trade_pos = None
            while trade_pos is None:
                # Find tanner
                tanner_pos = self.find_tanner()

                # Click on tanner
                bot.click_long(tanner_pos)
                trade_pos = self.session.find_in_client(TRADE_WITH_TANNER)
            return trade_pos
        
        click_on_tanner_event = Event([
            (click_on_tanner, None)
        ])
        self.session.publish_event(click_on_tanner_event)

        # TODO: Have the event manager return the value of the event
        trade_pos = click_on_tanner_event.action_returns[0]
        self.session.publish_event(Event([
            (Event.click(trade_pos), None)
        ]))

        while self.session.find_in_client(TANNER_OPEN) is None:
            debug("Tanner - tan_hides: Waiting for tanner menu to open")
            wait(.3, .6)

        # Click on leather portion
        self.session.publish_event(Event([
            (Event.click_long(self.session.translate(self.target_leather.random_point())), None)
        ]))

        # Click on 'all' on leather portion
        tan_all_pos = self.session.set_client_threshold(0.6).find_in_client(TAN_ALL)
        if trade_pos is None:
            error("failed to find the 'tan all' menu item so the bot is exiting. Should add a failure routine to try again...")
            self.session.exit()
            return
        self.session.publish_event(Event([
            (Event.click(tan_all_pos), None)
        ]))


    def find_tanner(self):
        tanner_pos = None
        while tanner_pos is None:
            frame = np.array(imlib.rescale_obj(grabber.grab(self.session.screen_bounds)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find tanner
            debug("Predicting...")
            predictions = TF_NET.return_predict(frame)
            bboxes = translate_predictions(predictions, return_as_box=True)
            print(bboxes)
            if len(bboxes) > 0:
                tanner_pos = self.session.translate(bboxes[0].center())
            else:
                # Spin camera
                bot.drag(*ui.spin_around(self.session))
                # self.session.publish_event(Event([
                #     (Event.drag(*ui.spin_around(self.session)), (.1, .2))
                # ]))

        return tanner_pos
