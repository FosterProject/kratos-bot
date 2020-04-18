import random

from PIL import Image

from tools.screen_pos import Pos
from tools.lib import pos_dist as dist


class Map():
    GOAL_A = ((255, 61, 200, 255), (124, 42, 91, 255))
    GOAL_B = ((94, 238, 255, 255), (0, 51, 255, 255))
    WALKABLE = ((7, 255, 36, 255), (32, 122, 0, 255))

    def __init__(self, map_path):
        self.grid = []
        self.read_in(map_path)
        self.grid_width = len(self.grid[0])
        self.grid_height = len(self.grid)

        self.start_tile = None
        self.end_tile = None

        self.path = None

    def read_in(self, img_path):
        img = Image.open(img_path)
        width, height = img.size
        for y in range(height):
            row = []
            for x in range(width):
                rgba = img.getpixel((x, y))
                goal = "A" if (rgba in Map.GOAL_A) else "B" if (
                    rgba in Map.GOAL_B) else None
                walkable = (rgba in Map.WALKABLE) or (goal in ("A", "B"))
                row.append(Tile(Pos(x + 1, y + 1), goal, walkable))
            self.grid.append(row)

    def build_path(self):
        if self.start_tile is None or self.end_tile is None:
            print("Error: Map must have a defined start and end tile")
            return

        # Preset start tile costs
        self.start_tile.gCost = 0
        self.start_tile.hCost = dist(self.start_tile.pos, self.end_tile.pos)

        open_set = []
        closed_set = []
        open_set.append(self.start_tile)

        while len(open_set) > 0:
            current_tile = open_set[0]
            for potential_tile in open_set:
                if (potential_tile.get_fCost() < current_tile.get_fCost()) or (potential_tile.get_fCost() == current_tile.get_fCost() and potential_tile.hCost < current_tile.hCost):
                    current_tile = potential_tile
            
            open_set.remove(current_tile)
            closed_set.append(current_tile)

            if current_tile == self.end_tile:
                self.retrace_path()
                return
            
            for neighbour in self.get_tile_neighbours(current_tile):
                if (neighbour.walkable != True) or (neighbour in closed_set):
                    continue

                new_movement_cost_to_neighbour = current_tile.gCost + dist(current_tile.pos, neighbour.pos)
                if new_movement_cost_to_neighbour < neighbour.gCost or neighbour not in open_set:
                    neighbour.gCost = new_movement_cost_to_neighbour
                    neighbour.hCost = dist(neighbour.pos, self.end_tile.pos)
                    neighbour.parent = current_tile

                    if neighbour not in open_set:
                        open_set.append(neighbour)

    
    def retrace_path(self):
        path = []
        current_tile = self.end_tile

        while current_tile != self.start_tile:
            current_tile.highlight = True
            path.append(current_tile)
            current_tile = current_tile.parent
        self.path = path.reverse()

    def get_tile_neighbours(self, tile):
        neighbours = []

        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                
                check_x = tile.pos.x + x
                check_y = tile.pos.y + y

                if check_x >= 0 and check_x <= self.grid_width and check_y >= 0 and check_y <= self.grid_height:
                    neighbours.append(self.grid[check_y - 1][check_x - 1])
        return neighbours

    def get_goal_tiles(self, goal):
        tiles = []
        for row in self.grid:
            for tile in row:
                if tile.goal == goal:
                    tiles.append(tile)
        return tiles

    def get_random_goal_tile(self, goal):
        return random.choice(self.get_goal_tiles(goal))

    def print(self):
        visual = ""
        for row in self.grid:
            for tile in row:
                visual = visual + tile.debug_str()
            visual = visual + "\n"
        print(visual)


class Tile():
    def __init__(self, pos, goal, walkable):
        self.pos = pos
        self.goal = goal
        self.walkable = walkable
        self.highlight = False  # Debugging only

        # Pathfinding
        self.gCost = 0  # Distance from start
        self.hCost = 0  # Distance from end
        self.parent = None

    def get_fCost(self):
        return self.gCost + self.hCost

    def debug_str(self):
        if self.highlight:
            return "@"
        if self.goal == "A":
            return "a"
        elif self.goal == "B":
            return "b"
        elif self.goal == None:
            if self.walkable:
                return "?"
            else:
                return "-"

    def __str__(self):
        return "Goal = %s | Pos: %s" % (self.goal, self.pos)
