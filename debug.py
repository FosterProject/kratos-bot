import time

print("starting")

try:
    while True:
        print("Processing...")
        # EVENT_MANAGER.process_event()
        time.sleep(.5)
except KeyboardInterrupt:
    pass

# Exit threads and bots
bots = [1,2,3]
for bot in bots:
    print(bot)
    # bot["bot"].session.exit()
    # bot["thread"].join()