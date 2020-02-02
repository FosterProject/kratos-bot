import pyautogui as bot
import random

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


def drag(start, end, time):
    bot.moveTo(start.x, start.y)
    bot.dragTo(end.x, end.y, time, bot.easeInQuad)