
from tools.event_manager import EventManager, Event
from tools.screen_pos import Pos
from tools.session import Session
from tools import config
config.DEBUG = True

session = Session(0, 0)
print("Session - has_pending_event: %s" % session.has_pending_event)

em = EventManager()
event = Event()
event.add_action(event.click(Pos(150, 150)), (3, 5))
em.add_event(session, event)
em.add_event(session, event)

print("Session - has_pending_event: %s" % session.has_pending_event)

em.process_event()

print("Session - has_pending_event: %s" % session.has_pending_event)











# from tools.session import Session
# from tools import osrs_screen_grab as grabber
# from tools.screen_pos import Pos, Box
# from tools import config
# config.DEBUG = True
# import pyautogui as bot

# from bots import mining
# from bots import bowstringer

# from utilities import account
# from utilities import ui
# from utilities import inventory
# from utilities import bank

# # from bots import mining
# from bots import bowstringer

# s = Session(0, 0)
# s2 = Session(0, 1)

# bank.find_booth(s2)