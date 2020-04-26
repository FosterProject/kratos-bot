from tools.screen_pos import Pos

BASE_PATH = "bot_ref_imgs/movement/"

# Movement Paths
MOVEMENT_BASE_PATH = BASE_PATH + "movement_paths/"
AL_KHARID_TANNER_PATH = MOVEMENT_BASE_PATH + "tanner_path.png"


# Grid Reference Images
REFERENCE_BASE_PATH = BASE_PATH + "grid_references/"
AL_KHARID_BANK_IMAGE = REFERENCE_BASE_PATH + "al_kharid_bank.png"
TANNER_BUILDING_IMAGE = REFERENCE_BASE_PATH + "tanner_building.png"

# Grid References
AL_KHARID_BANK_GRID = [
    [Pos(18, 3), None, None, Pos(30, 3)],
    [Pos(18, 7), None, None, Pos(30, 7)],
    [Pos(18, 11), None, None, Pos(30, 11)],
    [Pos(18, 15), Pos(22, 15), Pos(26, 15), Pos(30, 15)],
    [Pos(18, 19), Pos(22, 19), Pos(26, 19), None],
    [Pos(18, 23), Pos(22, 23), Pos(26, 23), Pos(30, 23)],
    [Pos(18, 27), Pos(22, 27), Pos(26, 27), Pos(30, 27)],
    [Pos(18, 31), Pos(22, 31), Pos(26, 31), Pos(30, 31)],
    [Pos(18, 35), Pos(22, 35), Pos(26, 35), Pos(30, 35)],
    [Pos(18, 39), Pos(22, 39), Pos(26, 39), Pos(30, 39)],
    [Pos(18, 43), Pos(22, 43), Pos(26, 43), None],
    [Pos(18, 46), Pos(22, 46), Pos(26, 46), Pos(30, 46)],
    [Pos(18, 50), None, Pos(26, 50), None]
]

AL_KHARID_TANNER_GRID = [
    [None, None, None, None, None, None, Pos(25, 2), None],
    [Pos(2, 6), None, None, None, Pos(17, 6), Pos(21, 6), Pos(25, 6), Pos(29, 6)],
    [Pos(2, 10), Pos(6, 10), Pos(10, 10), Pos(14, 10), Pos(17, 10), None, None, Pos(29, 10)],
    [Pos(2, 14), Pos(6, 14), Pos(10, 14), Pos(14, 14), Pos(17, 14), Pos(21, 14), Pos(25, 14), Pos(29, 14)],
    [Pos(2, 18), None, None, Pos(14, 18), None, None, None, Pos(25, 18), Pos(29, 18)],
    [None, Pos(6, 22), Pos(10, 22), Pos(10, 22), Pos(14, 22), Pos(17, 22), Pos(21, 22), Pos(25, 22), Pos(29, 22)]
]