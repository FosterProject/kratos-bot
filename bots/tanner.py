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
from tools import client_handler

# Data
from data import regions
from data.movement_references import AL_KHARID_TANNER_PATH
from data.movement_references import AL_KHARID_BANK_IMAGE
from data.movement_references import TANNER_BUILDING_IMAGE
from data.movement_references import AL_KHARID_BANK_GRID
from data.movement_references import AL_KHARID_TANNER_GRID

# Utilities
from utilities import account
from utilities import ui
from utilities import bank
from utilities import inventory
from utilities.items import Item
from utilities.map import Map


# Image References
UNTANNED_HIDE = Item("bot_ref_imgs/tanner/cowhide_short.png", .3)
TANNED_HIDE = Item("bot_ref_imgs/tanner/hard_leather.png", .3)
CASH_STACK_BANK = Item("bot_ref_imgs/tanner/cash_stack_bank.png", .3)

UNTANNED_HIDE_EMPTY = "bot_ref_imgs/tanner/cowhide_empty.png"

TRADE_WITH_TANNER = "bot_ref_imgs/tanner/trade_ellis.png"
TAN_OPTION_BOX = "bot_ref_imgs/tanner/tan_option_box.png"
TAN_ALL = "bot_ref_imgs/tanner/all.png"
TANNER_OPEN = "bot_ref_imgs/tanner/tanner_open.png"

# Positions (Unique to bot so not in grabber)
TANNING_INTERFACE = Box(Pos(130, 169), Pos(605, 461))
TAN_SOFT_LEATHER = Box(Pos(176, 231), Pos(228, 267))

# Movement
MOVEMENT = {
    "A": {
        "start_reference_image": TANNER_BUILDING_IMAGE,
        "start_reference_grid": AL_KHARID_TANNER_GRID,
        "starting_goal": "B"
    },
    "B": {
        "start_reference_image": AL_KHARID_BANK_IMAGE,
        "start_reference_grid": AL_KHARID_BANK_GRID,
        "starting_goal": "A"
    }
}
MOVE_TO_BANK = "A"
MOVE_TO_TANNER = "B"

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
        self.map = Map(AL_KHARID_TANNER_PATH, self.client.host)

        # Login timers
        self.min_login_time = 45 * 60
        self.max_login_time = 280 * 60
        self.min_logout_time = 5 * 60
        self.max_logout_time = 15 * 60

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

        # Check to see if started in al kharid bank

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
            move_result = self.move(MOVE_TO_TANNER)
            if move_result == False:
                self.client.log("Failed to execute move to tanner routine")
                sys.exit()
            wait(.6, .9)

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
                    self.client.log("Tried 7 times to tan hides and failed")
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
            move_result = self.move(MOVE_TO_BANK)
            if move_result == False:
                self.client.log("Failed to execute move to bank routine")
                sys.exit()
            wait(.6, .9)

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

                # Close bank
                bank.close(self.client)
                wait(.8, 1.2)

                # Logout
                self.client.info("... logging out ...")
                account.logout(self.client)

                # Sleep for logout time
                wait(self.min_logout_time, self.max_logout_time)

                self.client.info("... starting up again.")
                # Startup
                self.startup()

    def move(self, goal):
        while True:
            starting_tile_attempts = 0
            check = None
            while check is None and starting_tile_attempts < 5:
                starting_tile_attempts += 1
                local_pos = self.client.set_threshold(.45).find(MOVEMENT[goal]["start_reference_image"], regions.MAP, True)
                while local_pos is None:
                    self.client.log("Attempting to pinpoint starting tile")
                    local_pos = self.client.set_threshold(.45).find(MOVEMENT[goal]["start_reference_image"], regions.MAP, True)
                    wait(.3, .5)
                x = Map.CENTER.x - local_pos.tl.x
                y = Map.CENTER.y - local_pos.tl.y
                print(Pos(x, y))
                check = Map.find_pos_in_local_grid(Pos(x, y), MOVEMENT[goal]["start_reference_grid"])

                # Try adding 1 to x to see if that fixes the off by 1 weird error
                if check is None:
                    x += 1
                    check = Map.find_pos_in_local_grid(Pos(x, y), MOVEMENT[goal]["start_reference_grid"])

            if check is None:
                self.client.log("Movement - Not in expected starting tile, can't build (tried 5 times):: last check pos = %s" % Pos(x, y))
                return False
            
            # print(check)

            start_tile = self.map.translate_goal_region_pos_to_grid(MOVEMENT[goal]["starting_goal"], check)
            # print(start_tile)
            self.map.set_start_tile(start_tile)
            self.map.set_end_tile(self.map.get_random_goal_tile(goal))
            # print(self.map.end_tile)

            self.map.build_path()
            self.map.split_path()
            # self.map.print()  # Debug

            while not self.map.finished_route:
                self.map.move_to_next_checkpoint(self.client.client)
                while self.map.is_moving:
                    self.map.check_is_moving(self.client.host)
                    wait(.3, .5)
            self.map.reset_map()
            return True

    def bank_inventory(self):
        # Open bank
        if not bank.is_bank_open(self.client):
            bank.open(self.client)
            wait(1.5, 2.5)

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

            # Check that we are still in the tanner
            if self.is_in_tanner() is False:
                # True north
                ui.click_compass(self.client)
                wait(.2, .4)

                # Move back into tanner building
                tanner_building_pos = self.client.set_threshold(.45).find(MOVEMENT["A"]["start_reference_image"], regions.MAP, True).center()
                self.client.click(tanner_building_pos)

                # Wait until we stop moving
                self.map.is_moving = True
                while self.map.is_moving:
                    self.map.check_is_moving(self.client.host)
                    wait(.3, .5)
                self.map.reset_map()

                # wait(3, 5)  # TODO: Use the Map check_is_moving method to securely say we've finished moving

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
        option_box = None
        ob_attempts = 0
        while option_box is None and ob_attempts <= 3:
            ob_attempts += 1
            option_box = self.client.set_threshold(.8).find(
                TAN_OPTION_BOX, return_box=True)
        if option_box is None:
            self.client.log("failed to find the tan option box 3 times, bot is exiting.")
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

    def is_in_goal(self, goal):
        # Must be true north
        ui.click_compass(self.client)
        wait(.2, .4)

        local_pos = None
        find_attempts = 0
        while local_pos is None:
            local_pos = self.client.set_threshold(.45).find(MOVEMENT[goal]["start_reference_image"], regions.MAP, True)
            find_attempts += 1
            # Spin if local_pos is still None
            if local_pos is None:
                ui.spin_around(self.client)
                wait(1, 1.1)

        x = Map.CENTER.x - local_pos.tl.x
        y = Map.CENTER.y - local_pos.tl.y
        return Map.find_pos_in_local_grid(Pos(x, y), MOVEMENT[goal]["start_reference_grid"]) is not None

    def is_in_tanner(self):
        # Must be true north
        ui.click_compass(self.client)
        wait(.2, .4)

        local_pos = None
        find_attempts = 0
        while local_pos is None:
            local_pos = self.client.set_threshold(.45).find(MOVEMENT["A"]["start_reference_image"], regions.MAP, True)
            find_attempts += 1
            # Spin if local_pos is still None
            if local_pos is None:
                ui.spin_around(self.client)
                wait(1, 1.1)

        x = Map.CENTER.x - local_pos.tl.x
        y = Map.CENTER.y - local_pos.tl.y
        return Map.find_pos_in_local_grid(Pos(x, y), MOVEMENT["A"]["start_reference_grid"]) is not None
