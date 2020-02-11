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
from tools import config
config.DEBUG = True
from tools import osrs_screen_grab as grabber
from tools import image_lib as imlib
from tools.lib import wait
from tools.lib import debug
from tools.lib import error
from tools.lib import translate_predictions, translate_tracker
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
PICKAXE = Item("bot_ref_imgs/mining/pickaxe_mithril.png", .3)

# UI
MINING_SUCCESS = [
    "bot_ref_imgs/mining/copper_success.png",
    "bot_ref_imgs/mining/iron_success.png"
]
MINING_START = "bot_ref_imgs/mining/mining_start.png"
NO_ORE_AVAILABLE = "bot_ref_imgs/mining/no_ore_available.png"

# Movement Images
MOVEMENT_MINE_PATH = [
    "bot_ref_imgs/mining/movement/6.png",
    "bot_ref_imgs/mining/movement/5.png",
    [
        "bot_ref_imgs/mining/movement/4_0.png",
        "bot_ref_imgs/mining/movement/4_1.png",
    ],
    "bot_ref_imgs/mining/movement/3.png",
    "bot_ref_imgs/mining/movement/2.png",
    "bot_ref_imgs/mining/movement/1.png",
    "bot_ref_imgs/mining/movement/0.png",
]
MOVEMENT_BANK_PATH = [
    "bot_ref_imgs/mining/movement/0.png",
    "bot_ref_imgs/mining/movement/1.png",
    "bot_ref_imgs/mining/movement/2.png",
    "bot_ref_imgs/mining/movement/3.png",
    [
        "bot_ref_imgs/mining/movement/4_0.png",
        "bot_ref_imgs/mining/movement/4_1.png",
    ],
    "bot_ref_imgs/mining/movement/5.png",
    "bot_ref_imgs/mining/movement/6.png",
    "bot_ref_imgs/mining/movement/7.png",
]

# Positions (Unique to bot so not in grabber)

# Constants
MINING_WAIT_FOR_SUCCESS_MAX = 10
MINING_WAIT_FOR_START_MAX = 5

# Load Darkflow
TFNET_OPTIONS = {
    "pbLoad": "brain_mining_copper/yolo-kratos.pb",
    "metaLoad": "brain_mining_copper/yolo-kratos.meta",
    "labels": "brain_mining_copper/labels.txt",
    "threshold": 0.1
}
TF_NET = TFNet(TFNET_OPTIONS)


class Mining:
    def __init__(self, session, power=False):
        self.session = session

        # Movement
        self.mining_route = Movement(session, MOVEMENT_MINE_PATH)
        self.bank_route = Movement(session, MOVEMENT_BANK_PATH)

        # Login timers
        self.min_login_time = 15 * 60
        self.max_login_time = 280 * 60
        self.min_logout_time = 5 * 60
        self.max_logout_time = 50 * 60

        # Retrack rocks
        self.find_rocks_start_time = time.time()
        self.find_rocks_timer_cap = 20

        # Class Variables
        self.current_rock_index = None

    
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
        if bank.find_booth(self.session, "NORTH") is None:
            print("Kratos-Bot >> Please start this bot in Varrock East bank")
            sys.exit()

        # Open bank and empty inventory
        self.deposit_inventory()

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

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([(Event.click(compass_pos), (.5, .8))]))

            # Move to mine
            self.move(self.mining_route)

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([(Event.click(compass_pos), (.5, .8))]))

            # Spin camera
            self.session.publish_event(Event([
                (Event.drag(*ui.spin_around(self.session)), (.1, .2))
            ]))

            # Mine rocks until inventory is full
            self.mine_rocks()

            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([(Event.click(compass_pos), (.5, .8))]))

            # Move to bank
            self.move(self.bank_route)

            # Click compass
            compass_pos = ui.click_compass(self.session)
            self.session.publish_event(Event([(Event.click(compass_pos), (.5, .8))]))

            # Bank inventory
            self.deposit_inventory()

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
                (Event.click(step_pos), (.2, .5))
            ]))
            while route.is_moving:
                route.check_is_moving()
                wait(.2, .5)
        route.reset()


    def deposit_inventory(self):
        # Open bank
        if not bank.is_bank_open(self.session):
            booth_pos = bank.open(self.session, "NORTH")
            self.session.publish_event(Event([
                (Event.click(booth_pos), (.5, .8))
            ]))

        while not bank.is_bank_open(self.session):
            print("Waiting to open the bank")
            wait(.5, 1)

        # Event
        event = Event()

        # Empty inventory
        bank_inventory_pos = bank.bank_inventory(self.session)
        event.add_action(Event.click(bank_inventory_pos), (.8, 1.2))

        # Withdraw pickaxe
        pickaxe_pos = bank.withdraw_item(self.session, PICKAXE)
        event.add_action(Event.click(pickaxe_pos), (.5, .8))

        # Close the bank
        bank_close_pos = bank.close(self.session)
        if bank_close_pos is None:
            error("bot has fallen out of sync, it thinks the bank is open and when it isn't")
            return
        event.add_action(Event.click(bank_close_pos), (.8, 1.3))

        self.session.publish_event(event)


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


    # TODO: Check if moved using Movement class. If moved, re-find rocks else just use next rock in list.
    def mine_rocks(self):
        while True:
            inv_full = False
            no_ore_available = False
            failed_to_start = False

            rocks = self.find_rocks()
            rand_rock = rocks[random.randint(0, len(rocks) - 1)]
            # Mine a rock
            print("---------- MINING A FRESH ROCK ----------------")
            self.session.publish_event(Event([
                (Event.click(self.session.translate(rand_rock.random_point())), (.1, .15))
            ]))

            # Wait to start mining
            wait_to_start_timer = time.time()
            while self.session.set_region_threshold(0.6).find_in_region(grabber.CHAT_LAST_LINE, MINING_START) is None:
                print("mining start fail")
                if time.time() - wait_to_start_timer >= MINING_WAIT_FOR_START_MAX:
                    failed_to_start = True
                    break
                # If inventory full
                if ui.inventory_full(self.session):
                    inv_full = True
                    break
                # No ore
                if self.session.set_region_threshold(0.6).find_in_region(grabber.CHAT_LAST_LINE, NO_ORE_AVAILABLE) is not None:
                    no_ore_available = True
                    
                wait(.4, .6)

            if failed_to_start:
                print("Failed to start")
                continue
            if inv_full:
                print("Inventory full")
                break
            if no_ore_available:
                print("No ore available")
                continue

            # Check mining success
            mining_timer = time.time()
            mining_success = None
            while mining_success is None:
                print("looking for success")
                if time.time() - mining_timer >= MINING_WAIT_FOR_SUCCESS_MAX:
                    print("ran out of time, moving to new rock")
                    break
                for check in MINING_SUCCESS:
                    if self.session.set_region_threshold(0.6).find_in_region(grabber.CHAT_LAST_LINE, check) is not None:
                        mining_success = True
                        break

                wait(.4, .6)


    def find_rocks(self):
        trackers = []
        while len(trackers) < 1:
            frame = np.array(imlib.rescale_obj(grabber.grab(self.session.screen_bounds)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find rocks
            debug("Predicting...")
            predictions = TF_NET.return_predict(frame)
            bboxes = translate_predictions(predictions, return_as_box=True)

            if len(bboxes) > 0:
                return bboxes
            else:
                # Spin camera
                self.session.publish_event(Event([
                    (Event.drag(*ui.spin_around(self.session)), (.1, .2))
                ]))





    # TODO: Come back to this another day, trackers are losing themselves because of low FPS...
    def mine_rocks_tracker(self):
        rocks = self.find_rocks()

        fresh_rock = False
        while not ui.inventory_full(self.session):
            # Get next frame
            frame = np.array(imlib.rescale_obj(grabber.grab(self.session.screen_bounds)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Refresh trackers every x seconds
            if time.time() - self.find_rocks_start_time >= self.find_rocks_timer_cap:
                rocks = self.find_rocks()
                fresh_rock = True

            # Update trackers
            successful_rock_indexes = []
            for i, rock in enumerate(rocks):
                success, bbox = rock["tracker"].update(frame)
                rock["alive"] = success
                rock["box"] = Box(
                    imlib.upscale(Pos(
                        int(bbox[0]),
                        int(bbox[1])
                    )).add(Pos(imlib.left, imlib.upper)),
                    imlib.upscale(Pos(
                        int(bbox[0] + bbox[2]),
                        int(bbox[1] + bbox[3])
                    )).add(Pos(imlib.left, imlib.upper))
                )
            
                if success:
                    p1 = (int(bbox[0]), int(bbox[1]))
                    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                    cv2.rectangle(frame, p1, p2, (140, 1, 1), 2, 1)

                if success == True and i != self.current_rock_index:
                    successful_rock_indexes.append(i)


            # print("Rocks:")
            # print(rocks)
            print("Alive rock count: %s" % len(successful_rock_indexes))

            # Check if need to switch rocks
            if (self.current_rock_index is None or rocks[self.current_rock_index]["alive"] == False) and len(successful_rock_indexes) > 0:
                print("----- FRESH ROCK -----")
                self.current_rock_index = successful_rock_indexes[random.randint(0, len(successful_rock_indexes) - 1)]
                fresh_rock = True

            print("Current: %s || State: %s" % (self.current_rock_index, rocks[self.current_rock_index]["alive"]))
            # print("Successful: ")
            # print(successful_rock_indexes)

            # Mine a rock
            if fresh_rock:
                print("---------- MINING A FRESH ROCK ----------------")
                fresh_rock = False
                
                self.session.publish_event(Event([
                    (Event.click(self.session.translate(rocks[self.current_rock_index]["box"].random_point())), (.1, .15))
                ]))
            # wait(.1, .15)
            cv2.imshow('test', frame)
            if cv2.waitKey(2) & 0xFF == ord('q'):
                break


    #TODO: Tracker init ^ see above function
    def find_rocks_old(self):
        trackers = []
        while len(trackers) < 1:
            frame = np.array(imlib.rescale_obj(grabber.grab(self.session.screen_bounds)))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find rocks
            debug("Predicting...")
            predictions = TF_NET.return_predict(frame)
            bboxes = translate_tracker(predictions)


            if len(bboxes) > 0:
                # Initialise Multi-Tracker
                for bbox in bboxes:
                    tracker = cv2.TrackerKCF_create()
                    tracker.init(frame, bbox)
                    trackers.append({"tracker": tracker, "alive": True, "box": None})
                self.find_rocks_start_time = time.time()
                return trackers
            else:
                # Spin camera
                self.session.publish_event(Event([
                    (Event.drag(*ui.spin_around(self.session)), (.1, .2))
                ]))
