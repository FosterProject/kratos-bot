import sys
import time

from tools import client_handler


clients = client_handler.get_clients()
name, client, host = clients[0]


BASE_PATH = "F:/Development/Projects/Bots/RAW_DATA_BANK_AND_BUILDINGS/"

iteration = 0
while True:
    client_handler.screenshot(
        host, save=True, file_path="%s%s" % (BASE_PATH, iteration))
    iteration += 1
    time.sleep(.35)
