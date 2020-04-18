import win32con
import time

from tools import config
from tools.client import Client
from tools.screen_pos import Pos
from tools import client_handler
from data import regions
from debug import debug

from utilities import account
from utilities import ui
from utilities import bank
from utilities import inventory
from utilities import movement
from utilities.items import Item


debug.reset_stream()
config.DEBUG = True

clients = client_handler.get_clients()

name, client, host = clients[0]
# name2, client2, host2 = clients[1]
c = Client(name, client, host)
# c2 = Client(name2, client2, host2)

# Test area

kharid = [
    [Pos(18, 3), None, None, Pos(30, 3)],
    [Pos(18, 7), None, None, Pos(30, 7)],
    [Pos(18, 11), None, None, Pos(30, 11)],
    [Pos(18, 15), Pos(22, 15), Pos(26, 15), Pos(30, 15)],
    [Pos(18, 19), Pos(22, 19), Pos(26, 19), None],
    [Pos(18, 23), Pos(22, 23), Pos(26, 23), Pos(30, 23)],
    [Pos(18, 27), Pos(22, 27), Pos(26, 27), Pos(30, 27)],
    [Pos(18, 31), Pos(22, 31), Pos(26, 31), Pos(30, 31)],
    [Pos(18, 35), Pos(22, 35), Pos(26, 35), Pos(30, 35)],
    [Pos(18, 39), Pos(22, 39), Pos(26, 39), Pos(30, 39)],
    [Pos(18, 43), Pos(22, 43), Pos(26, 43), None],
    [Pos(18, 46), Pos(22, 46), Pos(26, 46), Pos(30, 46)],
    [Pos(18, 50), None, Pos(26, 50), None]
]

def find_pos(pos):
    y = 0
    for row in kharid:
        y += 1
        x = 0
        for item in row:
            x += 1
            if item is None:
                continue
            if pos.x == item.x and pos.y == item.y:
                return Pos(x, y)
    return None


center_x = 795
center_y = 83
while True:
    bank_pos = c.find("al_kharid_bank.png", regions.MAP, True)
    if bank_pos is None:
        print("Can't find bank")
    else:
        # check = bank_pos.contains(Pos(center_x, center_y))
        # print(check)

        x = center_x - bank_pos.tl.x
        y = center_y - bank_pos.tl.y
        check = find_pos(Pos(x, y))
        if check is None:
            print("Not in bank")
        else:
            print(check)
    time.sleep(.5)

# from bots import tanner
# bot = tanner.Tanner(c, tanner.TAN_SOFT_LEATHER)