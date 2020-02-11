import pyautogui as bot
import random
import time

from tools.screen_pos import Pos

# Mouse Movement
MOUSE_MIN_MOVE_TIME = .5
MOUSE_MAX_MOVE_TIME = 5


def click(pos):
    bot.moveTo(
        pos.x,
        pos.y,
        # round(random.uniform(MOUSE_MIN_MOVE_TIME, MOUSE_MIN_MOVE_TIME), 1)
        )
    bot.click()


def click_long(pos):
    bot.mouseDown(pos.x, pos.y)
    time.sleep(2)
    bot.mouseUp()


def type_string(string, send=False):
    bot.write(string)
    if send:
        press_enter()


def press_enter():
    bot.press("enter")


def press_space():
    bot.press("space")


def drag(start, end, time):
    bot.moveTo(start.x, start.y)
    bot.dragTo(end.x, end.y, time, bot.easeInQuad)