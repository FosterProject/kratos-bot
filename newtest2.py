import win32api
import win32gui
import win32con

import time


main = win32gui.FindWindow(None, "BlueStacks")
child = win32gui.GetWindow(main, win32con.GW_CHILD)
main2 = win32gui.FindWindow(None, "OSRS #2")
child2 = win32gui.GetWindow(main2, win32con.GW_CHILD)

win32api.PostMessage(child, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
time.sleep(1)
win32api.PostMessage(child, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
win32api.PostMessage(child, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
time.sleep(1)
win32api.PostMessage(child, win32con.WM_ACTIVATE, win32con.WA_INACTIVE, 0)