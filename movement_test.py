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
c = Client(name, client, host)


    
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

# Test area


# y
# 82 break point
# 83 - 86 nothing
# 87 - 90 - 1 - 4
# 91 - 94 - 2 - 8
# 95 - 98 - 3 - 12
# 99 - 102 - 4 - 16
# 103 - 105 - 5 - 20
# 106 - 110 - 6 - 23
# 111 - 114 - 7 - 28
# 115 - 117 - 8 - 32
# 119 - 121 - 9 - 36
# 122 - 125 - 10 - 39
# 126 - 129 - 11 - 43
# 130 - 133 - 12 - 47


# x
# 794 1 tile left
# 795 - 797 nothing
# 798 - 801 - 1 -- 3
# 802 - 806 - 2 -- 7
# 807 - 809 - 3 -- 12
# 810 - 813 - 4 -- 15
# 814 - 817 - 5 -- 19
# 818 - 821 - 6 -- 23
# 822 - 825 - 7 -- 27
# 826 - 829 - 8 -- 31
# 830 - 833 - 9 -- 35
# 834 - 837 - 10 -- 39
# 838 - 841 - 11 -- 43
# 842 - 845 - 12 -- 47
