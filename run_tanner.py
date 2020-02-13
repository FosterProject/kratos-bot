import sys
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


# Constants
EXIT_FLAG = False
def stop():
    global EXIT_FLAG
    EXIT_FLAG = True


bot_count = 1
# Arg parsing
if len(sys.argv) == 2:
    bot_count = int(sys.argv[1])
    if 1 > bot_count > 4:
        print("Error: bot count must be between 1 and 4")
        sys.exit()


# Sessions
sessions = []
for i in range(0, bot_count):
    sessions.append(Session(*config.BOTS[i]))


def exit_bot(bot):
    bot["bot"].session.exit()
    bot["thread"].join()


# Define bots
from bots import tanner
bots = []
for s in sessions:
    bots.append({"bot": tanner.Tanner(s, tanner.TAN_SOFT_LEATHER), "thread": None})

keyboard.on_press_key('esc', lambda event: stop())
for i in range(0, bot_count):
    keyboard.on_press_key('f%s' % str(i + 1), lambda event: exit_bot(bots[i]))

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
        time.sleep(.15)
except KeyboardInterrupt:
    pass

# Exit threads and bots
print("Shutting down bots... waiting for them to finish their loop")
for bot in bots:
    bot["bot"].session.exit()
    bot["thread"].join()
