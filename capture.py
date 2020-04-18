from tools.client import Client
from tools import client_handler as handler
from data import regions

clients = handler.get_clients()


handler.screenshot(clients[0][2], save=True, file_path="capture")