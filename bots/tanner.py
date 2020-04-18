# Base imports
import sys
import time
import random
import threading

# Darkflow
import matplotlib.pyplot as plt
from darkflow.net.build import TFNet
import cv2
import numpy as np

# Libraries
from debug import debug
from tools import image_lib as imlib
from tools.screen_pos import Pos, Box
from tools.lib import wait
from tools.lib import debug as console
from tools.lib import translate_predictions
from data import regions
from tools import client_handler

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
TAN_OPTION_BOX = "bot_ref_imgs/tanner/tan_option_box.png"
TAN_ALL = "bot_ref_imgs/tanner/all.png"
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
TANNING_INTERFACE = Box(Pos(130, 169), Pos(605, 461))
TAN_SOFT_LEATHER = Box(Pos(176, 231), Pos(228, 267))


# Load Darkflow
TFNET_OPTIONS = {
    "pbLoad": "brain_tanner/yolo-kratos.pb",
    "metaLoad": "brain_tanner/yolo-kratos.meta",
    "labels": "brain_tanner/labels.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)


TANNER_LOCK = threading.Lock()  # Lock for TF prediction
class Tanner:
    def __init__(self, client, target_leather):
        self.client = client
        self.target_leather = target_leather

        # Movement
        self.tanner_route = Movement(client, MOVEMENT_TANNER_PATH)
        self.bank_route = Movement(client, MOVEMENT_BANK_PATH)

        # Login timers
        self.min_login_time = 15 * 60
        self.max_login_time = 280 * 60
        self.min_logout_time = 5 * 60
        self.max_logout_time = 50 * 60

        # UI Timers
        self._true_north_timer = time.time()
        self._true_north_timer_cap = 14 * 60

    # Bot startup actions

    def startup(self):
        self.client.log("Kratos-Bot >> Running Tanner startup...")
        self.client.info("Running Tanner startup...")

        # Login
        account.login(self.client)
        wait(2, 3)

        # True north
        ui.click_compass(self.client)
        wait(.8, 1.1)

        # At bank check
        if bank.find_booth(self.client, "EAST") is None:
            self.client.log("Kratos-Bot >> Please start this bot in Al Kharid bank")
            sys.exit()

        # Open bank and empty inventory
        self.bank_inventory()
        wait(.7, 1.2)

        # Toggle select all
        bank.options_select_all(self.client)
        wait(.5, .8)

        # Setup login timers
        self.client.set_login_time_max(
            self.min_login_time, self.max_login_time)

    # Run bot

    def run(self):
        self.client.log("Kratos-Bot >> Running startup routine")
        self.startup()

        self.client.log("Kratos-Bot >> Starting main bot loop")
        while True:
            if self.client.should_exit():
                self.client.info("Exiting Tanner script.")
                self.client.log("[%s] - EXITING BOT LOOP" % self.client.name)
                break

            # Withdraw untanned hides
            self.client.info("Withdrawing hides")
            self.withdraw_resources()
            wait(1.1, 1.7)

            # Logout if out of resources
            out_of_resource = self.client.find(
                UNTANNED_HIDE_EMPTY, regions.BANK) is not None

            # Close the bank
            bank.close(self.client)
            if out_of_resource:
                # Close it a second time because interface interrupt
                bank.close(self.client)
            wait(.2, .4)

            # Log out checkpoint
            if out_of_resource:
                account.logout(self.client)
                self.client.exit()
                break

            # Full run
            if ui.run_full(self.client):
                ui.click_run_orb(self.client)
            wait(.2, .4)

            # Click compass
            ui.click_compass(self.client)
            wait(.2, .4)

            # Move to tanner
            self.client.info("Moving to Tanner")
            self.move(self.tanner_route)

            # Enable compass & two-step click
            ui.click_compass(self.client)
            wait(.2, .4)
            ui.click_tap_option(self.client, True)

            # Find tanner and tan hides
            self.client.info("Tanning hides")
            result = self.tan_hides()
            th_attempts = 0
            while result == "FAIL":
                th_attempts += 1
                result = self.tan_hides()
                if th_attempts >= 7:
                    self.client.log("Tried 3 times to tan hides and failed")
                    sys.exit()
                wait(1, 2)
            wait(.8, 1.3)

            # Disable compass & two-step click
            ui.click_compass(self.client)
            wait(.4, .6)
            ui.click_tap_option(self.client, False)
            wait(.3, .6)

            # Move to bank
            self.client.info("Moving to Bank")
            self.move(self.bank_route)
            wait(1.2, 1.8)

            # Click compass
            ui.click_compass(self.client)
            wait(.4, .6)

            # Bank inventory
            self.client.info("Banking inventory")
            self.bank_inventory()
            wait(.8, 1.3)

            # Check if we need to log out
            if self.client.should_log_out():
                self.client.info("Taking a break...")
                # Reset login timers
                self.client.set_login_time_max(
                    self.min_login_time, self.max_login_time)
                self.client.reset_login_time()

                # Logout
                self.client.info("... logging out ...")
                account.logout(self.client)

                # Sleep for logout time
                wait(self.min_logout_time, self.max_logout_time)

                self.client.info("... starting up again.")
                # Startup
                self.startup()

    def move(self, route):
        while not route.finished:
            route.step()
            while route.is_moving:
                route.check_is_moving()
                wait(.2, .5)
        route.reset()

    def bank_inventory(self):
        # Open bank
        if not bank.is_bank_open(self.client):
            bank.open(self.client, "EAST")
            wait(1.5, 2.5)

        idle_time = time.time()
        while not bank.is_bank_open(self.client):
            if time.time() - idle_time >= 6:
                ui.click_compass(self.client)
                bank.open(self.client, "EAST")
                wait(1.5, 2.5)
                idle_time = time.time()
            else:
                self.client.log("Waiting to open the bank")
                wait(.5, 1)

        # Empty inventory
        bank.bank_inventory(self.client)

    def withdraw_resources(self):
        bank.withdraw_item(self.client, UNTANNED_HIDE)

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
        # Click on trade with tanner
        trade_pos = None
        attempts = 0
        while trade_pos is None:
            if attempts >= 3:
                ui.spin_around(self.client)
                attempts = 0
            attempts += 1
            # Find tanner
            tanner_pos = self.find_tanner()

            # Click on tanner
            self.client.click(tanner_pos)
            wait(.5, .8)

            # Check if we managed to actually click on the tanner
            trade_pos = self.client.find(TRADE_WITH_TANNER)
            wait(.3, .6)

        # Trade with tanner
        self.client.click(trade_pos)
        wait(1.5, 2.5)

        to_attempts = 0
        while self.client.set_threshold(.3).find(TANNER_OPEN) is None:
            if to_attempts >= 3:
                return "FAIL"
            to_attempts += 1
            wait(2, 3)

        # Click on leather portion
        self.client.click(self.target_leather.random_point())
        wait(.7, 1.2)

        # Click on 'all' on leather portion
        self.click_tan_all()
        return None

    def click_tan_all(self):
        option_box = self.client.set_threshold(.8).find(
            TAN_OPTION_BOX, return_box=True)
        if option_box is None:
            self.client.log("failed to find the tan option box, bot is exiting.")
            self.client.exit()
            return

        allbox = option_box.copy()
        allbox.tl.add_raw(4, 98)
        allbox.br = allbox.tl.copy()
        allbox.br.add_raw(92, 20)
        self.client.click(allbox.random_point())

    def find_tanner(self):
        self.client.log("finding tanner")
        tanner_pos = None
        while tanner_pos is None:
            self.client.log("while start")
            frame = np.array(imlib.rescale_obj(
                client_handler.screenshot(self.client.host)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.client.log("before lock")

            # Find tanner
            with TANNER_LOCK:
                self.client.log("Predicting...")
                predictions = TF_NET.return_predict(frame)
            self.client.log("after lock")
            bboxes = translate_predictions(predictions, return_as_box=True)
            self.client.log("after bboxes")
            if len(bboxes) > 0:
                self.client.log("tanner found")
                tanner_pos = bboxes[0].center()
            else:
                self.client.log("spinning")
                # Spin camera
                ui.spin_around(self.client)
                wait(1, 1.1)

        self.client.log("returning tanner pos")
        return tanner_pos
