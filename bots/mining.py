# Base session
from tools.session import Session

# Utilities
from utilities import account

# Image References
COPPER = "bot_ref_imgs/quad_1080/mining/copper.png"
COPPER_BANK = "bot_ref_imgs/quad_1080/mining/copper_short.png"

class Mining:
    def __init__(self, session):
        self.session = session
