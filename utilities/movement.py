import sys

from tools import client_handler

WALK_DICT = {
    "x": {
        -12: 750,
        -11: 754,
        -10: 758,
        -9: 762,
        -8: 766,
        -7: 770,
        -6: 774,
        -5: 778,
        -4: 782,
        -3: 786,
        -2: 790,
        -1: 794,
        0: 797,
        1: 798,
        2: 802,
        3: 807,
        4: 811,
        5: 815,
        6: 819,
        7: 823,
        8: 827,
        9: 831,
        10: 835,
        11: 839,
        12: 843
    },
    "y": {
        -12: 131,
        -11: 127,
        -10: 123,
        -9: 119,
        -8: 115,
        -7: 111,
        -6: 107,
        -5: 103,
        -4: 99,
        -3: 95,
        -2: 91,
        -1: 87,
        0: 86,
        1: 82,
        2: 78,
        3: 74,
        4: 70,
        5: 66,
        6: 62,
        7: 58,
        8: 54,
        9: 50,
        10: 46,
        11: 42,
        12: 38
    }
}


def walk(client, x, y):
    if (x < -12 or x > 12) or (y < -12 or y > 12):
        print("Movement Error: Movement only handles walking +- 12 tiles on the x/y")
        sys.exit()

    xpos = WALK_DICT["x"][x]
    ypos = WALK_DICT["y"][y]

    client_handler.click(client, xpos, ypos)
