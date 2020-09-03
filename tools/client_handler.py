import time
import threading

import win32gui
import win32ui
import win32con
import win32api

from ctypes import windll
from PIL import Image

from debug import debug
from tools.screen_pos import Pos, Box


# USER DEFINED: Enter all client window names in this array
REGISTERED_CLIENTS = [
    "BlueStacks",
    # "OSRS #2",
    # "OSRS #3",
    # "OSRS #4"
]
# USER DEFINED: The default size of the host window
DEFAULT_HOST_SIZE_W = 880
DEFAULT_HOST_SIZE_H = 536
# USER DEFINED: The default size of the client window
DEFAULT_CLIENT_SIZE_W = 876
DEFAULT_CLIENT_SIZE_H = 492


def get_clients():
    """ Gets an array of all registered clients for win32api usage.

    Returns:
        array -- The array of win32 client codes.
    """

    clients = []

    for client in REGISTERED_CLIENTS:
        host = win32gui.FindWindow(None, client)
        if host == 0:
            debug.warn("Couldn't find registered client: %s" % client)
            continue
        game_window = win32gui.GetWindow(host, win32con.GW_CHILD)
        clients.append((client, game_window, host))
    return clients


def get_client_position(client):
    """ Returns the x/y top left position of a client.

    Arguments:
        client {int} -- The int value returned from a FindWindow win32gui call.

    Returns:
        dict{x, y} -- The x/y coords.
    """

    rect = win32gui.GetWindowRect(client)
    return {"x": rect[0], "y": rect[1]}


def get_client_dimensions(client):
    """ Returns the w/h of a client.

    Arguments:
        client {int} -- The int value returned from a FindWindow win32gui call.

    Returns:
        dict{w, h} -- The w/h values.
    """

    rect = win32gui.GetWindowRect(client)
    return {"w": rect[2] - rect[0], "h": rect[3] - rect[1]}


CLICK_LOCK = threading.Lock()


def click(client, x, y):
    """ Posts a click event to the client window.

    Arguments:
        client {int} -- The int value returned from a FindWindow win32gui call.
        x {int} -- The x position.
        y {int} -- The y position.
    """

    with CLICK_LOCK:
        pos = win32api.MAKELONG(x, y)

        win32api.PostMessage(client, win32con.WM_LBUTTONDOWN,
                             win32con.MK_LBUTTON, pos)
        time.sleep(.02)
        win32api.PostMessage(client, win32con.WM_LBUTTONUP,
                             win32con.MK_LBUTTON, pos)
        time.sleep(.05)


KEY_LOCK = threading.Lock()


def keypress(client, host, key):
    """ Posts a keydown event to the client window.
        This function 'activates' the client window so that it can accept a keyevent.

    Arguments:
        client {int} -- The int value returned from a FindWindow win32gui call.
        key {win32con.VK_*} -- The keycode of the key to be sent to the client. (Keycode should only be a constant from the win32con package).
    """

    with KEY_LOCK:
        delay = .15

        win32api.PostMessage(host, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        time.sleep(delay)
        win32api.PostMessage(client, win32con.WM_KEYDOWN, key, 0)
        time.sleep(.05)
        win32api.PostMessage(client, win32con.WM_KEYUP, key, 0)
        time.sleep(delay)
        win32api.PostMessage(host, win32con.WM_ACTIVATE,
                             win32con.WA_INACTIVE, 0)
        time.sleep(delay)


def default_host_size(host):
    """ Resizes and moves the host window to the default proportions defined in
        the constants:
            - DEFAULT_HOST_SIZE_W
            - DEFAULT_HOST_SIZE_H

    Arguments:
        host {int} -- The int value returned from a FindWindow win32gui call.
    """

    debug.info("Resizing host client [%s] to default position" % host)
    win32gui.MoveWindow(host, 0, 0, DEFAULT_HOST_SIZE_W,
                        DEFAULT_HOST_SIZE_H, True)


SCREENSHOT_LOCK = threading.Lock()


def screenshot(host, region=None, save=False, file_path=""):
    """ Takes a screenshot of a host window and crops it down to the client view.
        Returns the PIL.img variable or saves it to a file.

    Arguments:
        host {int} -- The int value returned from a FindWindow win32gui call.

    Keyword Arguments:
        save {bool} -- The flag to trigger a save action or not. (default: {False})
        file_path {str} -- The filepath to save the file to. (default: {"temp"})

    Returns:
        PIL.img OR None -- The img file if save=True.
    """

    with SCREENSHOT_LOCK:
        left, top, right, bot = win32gui.GetWindowRect(host)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(host)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitMap)

        result = windll.user32.PrintWindow(host, saveDC.GetSafeHdc(), 0)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(host, hwndDC)

        # PrintWindow Succeeded
        if result == 1:
            im = im.crop((2, 42, DEFAULT_CLIENT_SIZE_W +
                          2, DEFAULT_CLIENT_SIZE_H + 42))
            if region is not None:
                im = im.crop((region.tl.x, region.tl.y,
                              region.br.x, region.br.y))
            if save:
                loc = "%s_temp" % host if file_path == "" else file_path
                im.save("%s.png" % loc)
                return None
            else:
                return im
