from PIL import Image

from tools.screen_pos import Pos
from utilities import map as Map


IMG_PATH = "tanner_path_bitmap.png"


map = Map.Map(IMG_PATH)

# for i in range(3):
start_tile = map.get_random_goal_tile("A")
start_tile.highlight = True
map.start_tile = start_tile

end_tile = map.get_random_goal_tile("B")
end_tile.highlight = True
map.end_tile = end_tile

map.build_path()
map.split_path()
print("Start: %s - End: %s" % (map.start_tile.pos, map.end_tile.pos))
print("Steps: %s" % len(map.checkpoints))

while True:
    check = map.move_to_next_checkpoint()
    if not check:
        break

map.print()  # Debug

map.randomly_disable_path_tiles()
map.reset_map()