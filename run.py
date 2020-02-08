import threading
import time

from tools import config
from tools.session import Session
from tools.lib import wait

config.DEBUG = True



# Event Manager
from tools.event_manager import EventManager
EM = EventManager.get_instance()

# Sessions
s = Session(0, 0)
s2 = Session(0, 1)


# Define bots
from bots import bowstringer
from bots import tanner
bots = [
    {"bot": bowstringer.Bowstringer(s2), "thread": None},
    # {"bot": tanner.Tanner(s, tanner.TAN_SOFT_LEATHER), "thread": None}
]

# Run bots
for bot in bots:
    thread = threading.Thread(target=bot["bot"].run)
    bot["thread"] = thread
    thread.start()

try:
    while True:
        EM.process_event()
        time.sleep(.3)
except KeyboardInterrupt:
    pass

# Exit threads and bots
print("Shutting down bots... waiting for them to finish their loop")
for bot in bots:
    bot["bot"].session.exit()
    bot["thread"].join()
