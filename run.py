import threading

from tools import config
from tools.session import Session

config.DEBUG = True



# Event Manager
from tools import event_manager as em
EVENT_MANAGER = em.EventManager()

# Sessions
s2 = Session(0, 1)


# Define bots
from bots import bowstringer
bots = [
    {"bot": bowstringer.Bowstringer(s2), "thread": None}   
]

# Run bots
for bot in bots:
    bot["bot"].startup()
    thread = threading.Thread(target=bot["bot"].run)
    bot["thread"] = thread
    thread.start()


# Exit threads and bots
for bot in bots:
    bot["bot"].session.exit()
    bot["thread"].join()