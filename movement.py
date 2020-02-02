import cv2
import numpy as np
from matplotlib import pyplot as plt
import time

# Custom library
import tools.osrs_screen_grab as grabber
from tools.screen_pos import Pos
from tools import config
import bot

# Movement
IS_MOVING = False
MOVEMENT_IDLE_START_TIME = None
MOVEMENT_IDLE_MAX = 1.8
LAST_MAP = grabber.grab_region("", grabber.MAP).convert("L")


class Step:
    def __init__(self, path, weight):
        self.path = path
        self.weight = weight

STEPS = [
    Step("bot_ref_imgs/movement/0.png", 0),
    # Step("bot_ref_imgs/movement/1.png", 1),
    Step("bot_ref_imgs/movement/2.png", 2),
    Step("bot_ref_imgs/movement/3.png", 3),
    Step("bot_ref_imgs/movement/4.png", 4),
    Step("bot_ref_imgs/movement/5.png", 5),
    Step("bot_ref_imgs/movement/6.png", 6),
    [
        Step("bot_ref_imgs/movement/7.png", 7),
        Step("bot_ref_imgs/movement/7_1.png", 7),
        Step("bot_ref_imgs/movement/7_2.png", 7),
    ],
    Step("bot_ref_imgs/movement/8.png", 8),
    Step("bot_ref_imgs/movement/9.png", 9),
    Step("bot_ref_imgs/movement/10.png", 10)
]


def update_moving():
    global LAST_MAP
    global IS_MOVING
    global MOVEMENT_IDLE_START_TIME
    current_map = np.array(grabber.grab_region("", grabber.MAP).convert("L"))
    last_map_gray = np.array(LAST_MAP)

    w, h = current_map.shape[::-1]
    
    res = cv2.matchTemplate(last_map_gray, current_map, cv2.TM_CCOEFF_NORMED)
    threshold = 0.9
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(last_map_gray, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
    cv2.imwrite('debug/is_walking_outcome.png', last_map_gray)

    LAST_MAP = current_map
    if len(list(zip(*loc[::-1]))) < 1:
        set_is_moving(True)
    else:
        if MOVEMENT_IDLE_START_TIME is None:
            MOVEMENT_IDLE_START_TIME = time.time()

        if time.time() - MOVEMENT_IDLE_START_TIME >= MOVEMENT_IDLE_MAX:
            print("NOT MOVING")
            set_is_moving(False)



def set_is_moving(val):
    global IS_MOVING
    global MOVEMENT_IDLE_START_TIME
    IS_MOVING = val
    MOVEMENT_IDLE_START_TIME = None


def analyse_map(img_path):
    current_map = grabber.grab_region("current_map", grabber.MAP, True)
    current_map = cv2.imread(current_map)
    current_map_gray = cv2.cvtColor(current_map, cv2.COLOR_BGR2GRAY)
    step_template = cv2.imread(img_path, 0)

    w, h = step_template.shape[::-1]

    res = cv2.matchTemplate(current_map_gray, step_template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)


    # Debug
    if config.DEBUG:
        for pt in zip(*loc[::-1]):
            cv2.rectangle(current_map, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
        cv2.imwrite('debug/current_map_outcome.png', current_map)

    if len(list(zip(*loc[::-1]))) < 1:
        return False, None, w, h
    else:
        return True, zip(*loc[::-1]), w, h
    


def bank_path(reverse=False):
    global IS_MOVING
    
    # Reverse direction
    if reverse:
        track = STEPS.copy()
        track.reverse()
        track.pop(0)
    else:
        track = STEPS
    
    print("Starting banking rountine...")
    for step in track:
        weight = step.weight if not isinstance(step, list) else step[0].weight
        print("Attempting to move to step: %s" % weight)

        # Check for movement options
        success = False
        while success is False and IS_MOVING is False:
            if isinstance(step, list):
                for substep in step:
                    print("Checking substep: %s" % substep.path)
                    success, vals, w, h = analyse_map(substep.path)
                    if success:
                        continue
            else:
                success, vals, w, h = analyse_map(step.path)

        IS_MOVING = True
        for pt in vals:
            bot.click(Pos(
                grabber.MAP["TL"].x + pt[0] + (w / 2),
                grabber.MAP["TL"].y + pt[1] + (h / 2)
            ))
            break

        # Check if stopped
        while IS_MOVING is True:
            update_moving()


# Depricated
def move(step):
    current_map = grabber.grab_region("current_map", grabber.MAP, True)
    current_map = cv2.imread(current_map)
    current_map_gray = cv2.cvtColor(current_map, cv2.COLOR_BGR2GRAY)
    step_template = cv2.imread(step.path, 0)

    w, h = step_template.shape[::-1]

    res = cv2.matchTemplate(current_map_gray, step_template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        bot.click(Pos(
            grabber.MAP["TL"].x + pt[0] + (w / 2),
            grabber.MAP["TL"].y + pt[1] + (h / 2)
        ))
        cv2.rectangle(current_map, pt, (pt[0] + w, pt[1] + h), (25, 0, 255), 2)
        break


    cv2.imwrite('debug/current_map_outcome.png', current_map)