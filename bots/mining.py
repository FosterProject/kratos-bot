# Base session
from tools.session import Session

# Utilities
from utilities import account
from utilities.items import Item

# Image References
COPPER = Item("bot_ref_imgs/quad_1080/mining/copper.png", 0.3)
COPPER_BANK = Item("bot_ref_imgs/quad_1080/mining/copper_short.png", 0.3)

class Mining:
    def __init__(self, session):
        self.session = session
