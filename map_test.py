from PIL import Image

from tools.screen_pos import Pos
from utilities import map as Map


IMG_PATH = "tanner_path_bitmap.png"


map = Map.Map(IMG_PATH)

start_tile = map.get_random_goal_tile("A")
start_tile.highlight = True
map.start_tile = start_tile

end_tile = map.get_random_goal_tile("B")
end_tile.highlight = True
map.end_tile = end_tile

map.build_path()

print(map.path)

# Debug
map.print()