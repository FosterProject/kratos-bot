import threading
import time

import keyboard

from tools import config
from tools.session import Session
from tools.lib import wait

config.DEBUG = True



# Event Manager
from tools.event_manager import EventManager
EM = EventManager.get_instance()

EXIT_FLAG = False
def stop():
    global EXIT_FLAG
    EXIT_FLAG = True

# Sessions
s = Session(0, 0)
s2 = Session(0, 1)
s3 = Session(1, 0)


# Define bots
from bots import tanner
bots = [
    {"bot": tanner.Tanner(s, tanner.TAN_SOFT_LEATHER), "thread": None},
    # {"bot": tanner.Tanner(s2, tanner.TAN_SOFT_LEATHER), "thread": None},
    # {"bot": tanner.Tanner(s3, tanner.TAN_SOFT_LEATHER), "thread": None}
]

def exit_bot(bot):
    bot["bot"].session.exit()
    bot["thread"].join()

# Set up keyboard hooks
keyboard.on_press_key('esc', lambda event: stop())
keyboard.on_press_key('f1', lambda event: exit_bot(bots[0]))
keyboard.on_press_key('f2', lambda event: exit_bot(bots[1]))
keyboard.on_press_key('f3', lambda event: exit_bot(bots[2]))

# Run bots
for bot in bots:
    thread = threading.Thread(target=bot["bot"].run)
    bot["thread"] = thread
    thread.start()

try:
    while True:
        if EXIT_FLAG:
            print("Shutting down Kratos-bot")
            break
        EM.process_event()
        time.sleep(.1)
except KeyboardInterrupt:
    pass

# Exit threads and bots
print("Shutting down bots... waiting for them to finish their loop")
for bot in bots:
    bot["bot"].session.exit()
    bot["thread"].join()
