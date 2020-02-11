import cv2
import numpy as np
import time

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
from tools import config
from tools import bot
from tools.lib import debug


# Image References
MOVEMENT_FLAG = "bot_ref_imgs/movement/movement_flag.png"

# Constants
MOVEMENT_IDLE_TIME_MAX = 2

class Step:
    def __init__(self, path, weight):
        self.path = path
        self.weight = weight


class Movement:
    def __init__(self, session, steps):
        self.session = session
        self.steps = steps
        self.current_step = 0
        self.finished = False

        self.last_map = np.array(grabber.grab(session.screen_bounds, grabber.MAP).convert("L"))
        self.is_moving = False
        self.movement_idle_start_time = None


    def step(self):
        step = self.steps[self.current_step]
        if isinstance(step, list):
            for step_obj in step:
                step_pos = self.session.set_region_threshold(0.6).find_in_region(grabber.MAP, step_obj)
                if step_pos is not None:
                    break
        else:
            step_pos = self.session.find_in_region(grabber.MAP, step)

        # Set current step to next step
        self.current_step += 1
        if self.current_step == len(self.steps):
            self.finished = True
        
        self.is_moving = True
        self.movement_idle_start_time = None
        return step_pos
    

    def check_is_moving(self):
        debug("Movement - check_is_moving")

        current_map = np.array(grabber.grab(self.session.screen_bounds, grabber.MAP).convert("L"))
        res = cv2.matchTemplate(self.last_map, current_map, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)

        self.last_map = current_map
        
        if len(list(zip(*loc[::-1]))) < 1:
            self.movement_idle_start_time = None
            print("moving")
        else:
            print("still")
            if self.movement_idle_start_time is None:
                self.movement_idle_start_time = time.time()
            if time.time() - self.movement_idle_start_time >= MOVEMENT_IDLE_TIME_MAX:
                debug("Movement - NOT MOVING ANYMORE")
                self.is_moving = False





    def reset(self):
        self.current_step = 0
        self.finished = False
