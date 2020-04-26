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
from utilities.map import Map

debug.reset_stream()
config.DEBUG = True

clients = client_handler.get_clients()
name, client, host = clients[0]
c = Client(name, client, host)

client_handler.default_host_size(host)

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


IMG_PATH = "tanner_path_bitmap.png"
map = Map(IMG_PATH, host)

bank_pos = c.find("al_kharid_bank.png", regions.MAP, True)
if bank_pos is None:
    print("Can't find bank")
    exit()

x = Map.CENTER.x - bank_pos.tl.x
y = Map.CENTER.y - bank_pos.tl.y
check = find_pos(Pos(x, y))
if check is None:
    print("Not in bank")
    exit()


start_tile = map.translate_goal_region_pos_to_grid("A", check)
map.set_start_tile(start_tile)
map.set_end_tile(map.get_random_goal_tile("B"))

map.build_path()
map.split_path()
map.print()


while not map.finished_route:
    map.move_to_next_checkpoint(client)
    while map.is_moving:
        map.check_is_moving(host)
        time.sleep(.5)
map.reset_map()

print("done")





# while True:
#     bank_pos = c.find("al_kharid_bank.png", regions.MAP, True)
#     if bank_pos is None:
#         print("Can't find bank")
#     else:
#         # check = bank_pos.contains(Pos(center_x, center_y))
#         # print(check)

#         x = Map.CENTER.x - bank_pos.tl.x
#         y = Map.CENTER.y - bank_pos.tl.y
#         check = find_pos(Pos(x, y))
#         if check is None:
#             print("Not in bank")
#         else:
#             print(check)
#     time.sleep(.5)

# from bots import tanner
# bot = tanner.Tanner(c, tanner.TAN_SOFT_LEATHER)