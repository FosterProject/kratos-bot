import time

import win32gui
import win32con
import win32api


# main = win32gui.FindWindow(None, "*Untitled - Notepad")

main = win32gui.FindWindow(None, "BlueStacks")
child = win32gui.GetWindow(main, win32con.GW_CHILD)
print(child)
main2 = win32gui.FindWindow(None, "OSRS #2")
child2 = win32gui.GetWindow(main2, win32con.GW_CHILD)
print(child2)



print(win32gui.GetWindowRect(main2))
print(win32gui.GetWindowRect(child2))

exit()


# Screenshot testing
import win32ui
from ctypes import windll
from PIL import Image

hwnd = main2

# Change the line below depending on whether you want the whole window
# or just the client area. 
left, top, right, bot = win32gui.GetClientRect(hwnd)
# left, top, right, bot = win32gui.GetWindowRect(hwnd)
w = right - left
h = bot - top

hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

saveDC.SelectObject(saveBitMap)

# Change the line below depending on whether you want the whole window
# or just the client area. 
result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
# result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
print(result)

bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)

im = Image.frombuffer(
    'RGB',
    (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
    bmpstr, 'raw', 'BGRX', 0, 1)

win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)

if result == 1:
    #PrintWindow Succeeded
    im.save("test.png")
















# import win32gui
# import win32con

# def get_windows():
#     def sort_windows(windows):
#         sorted_windows = []

#         # Find the first entry
#         for window in windows:
#             if window["hwnd_above"] == 0:
#                 sorted_windows.append(window)
#                 break
#         else:
#             raise(IndexError("Could not find first entry"))

#         # Follow the trail
#         while True:
#             for window in windows:
#                 if sorted_windows[-1]["hwnd"] == window["hwnd_above"]:
#                     sorted_windows.append(window)
#                     break
#             else:
#                 break

#         # Remove hwnd_above
#         for window in windows:
#             del(window["hwnd_above"])

#         return sorted_windows

#     def enum_handler(hwnd, results):
#         window_placement = win32gui.GetWindowPlacement(hwnd)
#         results.append({
#             "hwnd":hwnd,
#             "hwnd_above":win32gui.GetWindow(hwnd, win32con.GW_HWNDPREV), # Window handle to above window
#             "title":win32gui.GetWindowText(hwnd),
#             "visible":win32gui.IsWindowVisible(hwnd) == 1,
#             "minimized":window_placement[1] == win32con.SW_SHOWMINIMIZED,
#             "maximized":window_placement[1] == win32con.SW_SHOWMAXIMIZED,
#             "rectangle":win32gui.GetWindowRect(hwnd) #(left, top, right, bottom)
#         })

#     enumerated_windows = []
#     win32gui.EnumWindows(enum_handler, enumerated_windows)
#     return sort_windows(enumerated_windows)

# if __name__ == "__main__":
#     windows = get_windows()

#     for window in windows:
#         print(window)
#     print()

#     # Pretty print
#     for window in windows:
#         if window["title"] == "" or not window["visible"]:
#             continue
#         print(window)
