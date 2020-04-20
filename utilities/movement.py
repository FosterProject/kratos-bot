from tools import client_handler

WALK_DICT = {
    "x": {
        0: 0,
        1: 3,
        2: 7,
        3: 12,
        4: 15,
        5: 19,
        6: 23,
        7: 27,
        8: 31,
        9: 35,
        10: 39,
        11: 43,
        12: 47
    },
    "y": {
        0: 0,
        1: 4,
        2: 8,
        3: 12,
        4: 16,
        5: 20,
        6: 23,
        7: 28,
        8: 32,
        9: 36,
        10: 39,
        11: 43,
        12: 47
    }
}

def walk(client, x, y):
    center_x = 795
    center_y = 83
    xpos = center_x - WALK_DICT["x"][abs(x)] if x < 0 else center_x + WALK_DICT["x"][x]
    ypos = center_y - WALK_DICT["y"][abs(y)] if y < 0 else center_y + WALK_DICT["y"][y]

    client_handler.click(client, xpos, ypos)