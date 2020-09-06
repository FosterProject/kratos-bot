import random
import time

import cv2
import numpy as np
from PIL import Image

from tools import client_handler
from tools.screen_pos import Pos
from tools.lib import pos_dist as dist

from data import regions

from utilities import movement


class Map():
    GOAL_A = ((255, 61, 200, 255), (124, 42, 91, 255))
    GOAL_B = ((94, 238, 255, 255), (0, 51, 255, 255))
    WALKABLE = ((7, 255, 36, 255), (32, 122, 0, 255))

    CENTER = Pos(795, 83)

    MAX_SECTION_LENGTH = 11
    MIN_SECTION_LENGTH = 8

    # Movement
    MOVEMENT_IDLE_TIME_MAX = 1.5

    def __init__(self, map_path, host):
        self.grid = []
        self.read_in(map_path)
        self.grid_width = len(self.grid[0])
        self.grid_height = len(self.grid)

        self.start_tile = None
        self.end_tile = None
        self.path = None
        self.checkpoints = []

        self.current_checkpoint = None

        # Movement
        self.finished_route = False
        self.last_map = self.get_map(host)
        self.is_moving = False
        self.movement_idle_start_time = None

    def set_start_tile(self, tile):
        self.start_tile = tile
        self.start_tile.highlight = True

    def set_end_tile(self, tile):
        self.end_tile = tile
        self.end_tile.highlight = True

    def read_in(self, img_path):
        img = Image.open(img_path)
        width, height = img.size
        for y in range(height):
            row = []
            for x in range(width):
                rgba = img.getpixel((x, y))
                goal = "A" if (rgba in Map.GOAL_A) else "B" if (
                    rgba in Map.GOAL_B) else None
                walkable = (rgba in Map.WALKABLE) or (rgba in (Map.GOAL_A[0], Map.GOAL_B[0]))
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
                print("Map:: Retracing path")
                self.retrace_path()
                return

            for neighbour in self.get_tile_neighbours(current_tile):
                if (neighbour.walkable != True) or (neighbour in closed_set) or (neighbour.disabled):
                    continue

                new_movement_cost_to_neighbour = current_tile.gCost + \
                    dist(current_tile.pos, neighbour.pos)
                if new_movement_cost_to_neighbour < neighbour.gCost or neighbour not in open_set:
                    neighbour.gCost = new_movement_cost_to_neighbour
                    neighbour.hCost = dist(neighbour.pos, self.end_tile.pos)
                    neighbour.parent = current_tile

                    if neighbour not in open_set:
                        open_set.append(neighbour)

    def retrace_path(self):
        tPath = []
        current_tile = self.end_tile

        while current_tile != self.start_tile:
            current_tile.highlight = True
            tPath.append(current_tile)
            current_tile = current_tile.parent
        tPath.reverse()
        self.path = tPath

    def split_path(self):
        total = len(self.path)

        self.start_tile.highlight_checkpoint = True
        self.checkpoints.append(self.start_tile)

        current = 0
        finished = False
        while not finished:
            current_section_length = random.randint(
                Map.MIN_SECTION_LENGTH, Map.MAX_SECTION_LENGTH)
            current = current + current_section_length
            if current >= total or (current < total and dist(self.path[current].pos, self.end_tile.pos) < Map.MAX_SECTION_LENGTH):
                self.end_tile.highlight_checkpoint = True
                self.checkpoints.append(self.end_tile)
                finished = True
            else:
                self.path[current].highlight_checkpoint = True
                self.checkpoints.append(self.path[current])

        self.current_checkpoint = 0

    def move_to_next_checkpoint(self, client):
        next_checkpoint = self.current_checkpoint + 1
        if next_checkpoint >= len(self.checkpoints) - 1:
            print("Finished route")
            self.finished_route = True
        current_pos = self.checkpoints[self.current_checkpoint].pos
        next_pos = self.checkpoints[next_checkpoint].pos

        move_x = next_pos.x - current_pos.x
        move_y = current_pos.y - next_pos.y

        self.current_checkpoint = next_checkpoint

        print("X: %s, Y: %s -- [%s, %s]" %
              (move_x, move_y, current_pos, next_pos))

        self.is_moving = True
        self.movement_idle_start_time = None
        movement.walk(client, move_x, move_y)

    def randomly_disable_path_tiles(self):
        for i, tile in enumerate(self.path):
            if tile == self.start_tile or tile == self.end_tile or tile.is_goal() or (i > 0 and self.path[i-1].disabled):
                continue
            if random.randint(1, 10) < 8:
                tile.disable()

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
                if tile.goal == goal and tile.walkable:
                    tiles.append(tile)
        return tiles

    def get_random_goal_tile(self, goal):
        return random.choice(self.get_goal_tiles(goal))

    def get_tl_goal_tile(self, goal):
        for row in self.grid:
            for tile in row:
                if tile.goal == goal:
                    return tile

    def reset_map(self):
        self.start_tile = None
        self.end_tile = None
        self.path = None
        self.current_checkpoint = None
        self.checkpoints = []
        self.finished_route = False
        self.is_moving = False
        for row in self.grid:
            for tile in row:
                tile.reset()

    def translate_goal_region_pos_to_grid(self, goal, rPos):
        reference_tile = self.get_tl_goal_tile(goal)
        pos = Pos(reference_tile.pos.x + (rPos.x - 1), reference_tile.pos.y + (rPos.y - 1))
        return self.get_tile_from_pos(pos)

    def get_tile_from_pos(self, pos):
        for row in self.grid:
            for tile in row:
                if tile.pos.x == pos.x and tile.pos.y == pos.y:
                    return tile

    def print(self):
        visual = ""
        for row in self.grid:
            for tile in row:
                visual = visual + tile.debug_str()
            visual = visual + "\n"
        print(visual)

    # Movement
    def check_is_moving(self, host):
        current_map = self.get_map(host)
        res = cv2.matchTemplate(
            self.last_map, current_map, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        loc = np.where(res >= threshold)

        self.last_map = current_map

        if len(list(zip(*loc[::-1]))) < 1:
            self.movement_idle_start_time = None
        else:
            if self.movement_idle_start_time is None:
                self.movement_idle_start_time = time.time()
            if time.time() - self.movement_idle_start_time >= Map.MOVEMENT_IDLE_TIME_MAX:
                print("Movement - NOT MOVING ANYMORE")
                self.is_moving = False

    def get_map(self, host):
        return np.array(client_handler.screenshot(host, regions.MAP).convert("L"))


    @staticmethod
    def find_pos_in_local_grid(pos, local_grid):
        y = 0
        for row in local_grid:
            y += 1
            x = 0
            for item in row:
                x += 1
                if item is None:
                    continue
                if pos.x == item.x and pos.y == item.y:
                    return Pos(x, y)
        return None

class Tile():
    def __init__(self, pos, goal, walkable):
        self.pos = pos
        self.goal = goal
        self.walkable = walkable
        self.highlight = False  # Debugging only
        self.highlight_checkpoint = False  # Debugging only

        # Pathfinding
        self.gCost = 0  # Distance from start
        self.hCost = 0  # Distance from end
        self.parent = None
        self.disabled = False

    def get_fCost(self):
        return self.gCost + self.hCost

    def is_goal(self):
        return self.goal == "A" or self.goal == "B"

    def disable(self):
        self.disabled = True

    def reset(self):
        self.highlight = False
        self.highlight_checkpoint = False
        self.parent = None

    def debug_str(self):
        if self.highlight_checkpoint:
            return "@"
        elif self.highlight:
            return " "
        elif self.goal == "A":
            if not self.walkable:
                return "A"
            return "a"
        elif self.goal == "B":
            if not self.walkable:
                return "B"
            return "b"
        elif self.goal == None:
            if self.walkable:
                return "?"
            else:
                return "-"

    def __str__(self):
        return "Goal = %s | Pos: %s" % (self.goal, self.pos)
