from tools.client import Client
from tools import client_handler as handler
from data import regions

clients, hosts = handler.get_clients()


handler.screenshot(hosts[0], save=True, file_path="capture")