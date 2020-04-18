import cv2
import numpy as np
import time

# Custom library
from tools import config
from tools.lib import debug as console
from data import regions
from tools import client_handler


# Image References
MOVEMENT_FLAG = "bot_ref_imgs/movement/movement_flag.png"

# Constants
MOVEMENT_IDLE_TIME_MAX = 2


class Step:
    def __init__(self, path, weight):
        self.path = path
        self.weight = weight


class Movement:
    def __init__(self, client, steps):
        self.client = client
        self.steps = steps
        self.current_step = 0
        self.finished = False

        self.last_map = self.get_map()
        self.is_moving = False
        self.movement_idle_start_time = None

    def step(self):
        step = self.steps[self.current_step]
        step_pos = self.find_step(step)

        # Set current step to next step
        self.current_step += 1
        if self.current_step == len(self.steps):
            self.finished = True

        self.is_moving = True
        self.movement_idle_start_time = None
        self.client.click(step_pos)

    def find_step(self, step):
        if not isinstance(step, list):
            step = [step]
        step_pos = None
        while step_pos is None:
            for step_obj in step:
                step_pos = self.client.set_threshold(
                    0.6).find(step_obj, regions.MAP)
                if step_pos is not None:
                    break

        return step_pos

    def check_is_moving(self):
        current_map = self.get_map()
        res = cv2.matchTemplate(
            self.last_map, current_map, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)

        self.last_map = current_map

        if len(list(zip(*loc[::-1]))) < 1:
            self.movement_idle_start_time = None
        else:
            if self.movement_idle_start_time is None:
                self.movement_idle_start_time = time.time()
            if time.time() - self.movement_idle_start_time >= MOVEMENT_IDLE_TIME_MAX:
                console("Movement - NOT MOVING ANYMORE")
                self.is_moving = False

    def get_map(self):
        return np.array(client_handler.screenshot(self.client.host, regions.MAP).convert("L"))

    def reset(self):
        self.current_step = 0
        self.finished = False
