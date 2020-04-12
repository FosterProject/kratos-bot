from tools.client import Client
from tools import client_handler as handler

clients, hosts = handler.get_clients()

c = Client(clients[0], hosts[0])

