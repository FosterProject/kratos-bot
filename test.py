import win32con
import time

from tools import config
from tools.client import Client
from tools import client_handler as handler
from data import regions
from debug import debug

from utilities import account
from utilities import ui
from utilities import bank
from utilities import inventory
from utilities.items import Item

debug.reset_stream()
config.DEBUG = True

clients, hosts = handler.get_clients()

c = Client("TEST", clients[0], hosts[0])

# Test area

# i = Item("bot_ref_imgs/tanner/cowhide_short.png", .15)

inventory.click_slot(c, 20)