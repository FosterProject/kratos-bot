# Base session
from tools.session import Session

# Utilities
from utilities import account
from utilities.items import Item

# Image References
COPPER = Item("bot_ref_imgs/mining/copper.png", 0.3)
COPPER_BANK = Item("bot_ref_imgs/mining/copper_short.png", 0.6)

class Mining:
    def __init__(self, session):
        self.session = session
