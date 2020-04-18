import win32con

# Custom library
from data import regions
from debug import debug
from tools.lib import debug as console
from tools.lib import wait

# Utilities
from utilities import ui


# Images
LOGOUT_CHECK = "bot_ref_imgs/account/logout_check.png"
TAP_TO_PLAY = "bot_ref_imgs/account/tap_to_play.png"
CONNECTING_CHECK = "bot_ref_imgs/account/connecting_check.png"
LOGOUT_INACTIVE = "bot_ref_imgs/account/logout_inactive.png"


def is_logged_out(client):
    check = client.find(LOGOUT_CHECK)
    return check is not None


def is_in_lobby(client):
    check = client.find(TAP_TO_PLAY)
    return check is not None


def is_connecting(client):
    check = client.find(CONNECTING_CHECK)
    return check is None


def login(client):
    if not is_logged_out(client):
        console("Client [%s] already logged in" % client.name)
        return

    client.info("Logging in")

    # Send login action
    client.key(win32con.VK_RETURN)

    # Enter game
    while not is_in_lobby(client):
        wait(1.5, 2)
        # If connection failed
        if not is_connecting(client):
            client.log("Attempting to log in again...")
            # Log in again
            client.key(win32con.VK_RETURN)
    
    # Enter through lobby
    client.click(regions.LOBBY_BUTTON.random_point())


def logout(client):
    if is_logged_out(client):
        console("Client [%s] already logged out" % client.name)
        return

    client.info("Logging out")

    click_pos = client.set_threshold(.8).find(LOGOUT_INACTIVE)
    if click_pos is not None:
        console("Account: Opening logout tab")
        ui.open_tab(client, "RIGHT", 6)
        
    wait(.8, 1.4)

    # Click logout button
    client.click(regions.LOGOUT_BUTTON.random_point())
