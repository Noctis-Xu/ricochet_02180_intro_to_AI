"""
The coordinate system follows Pygame's convention:
- The first value (x) represents the horizontal coordinate.
- The second value (y) represents the vertical coordinate.
"""

# Directions
NORTH = 'N'
EAST = 'E'
SOUTH = 'S'
WEST = 'W'
DIRECTIONS = [NORTH, EAST, SOUTH, WEST]
REVERSE = {NORTH: SOUTH, EAST: WEST, SOUTH: NORTH, WEST: EAST}

OFFSET = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}
# Colors
RED = 'R'
GREEN = 'G'
BLUE = 'B'
YELLOW = 'Y'
COLORS = [RED, GREEN, BLUE, YELLOW]

# Game
class Game(object):
    @staticmethod
    def hardest():
        grid = [
            ['NW', 'N', 'N', 'N', 'NE', 'NW', 'N', 'N', 'N', 'EN', 'WN', 'N', 'N', 'N', 'NS', 'EN'],
            ['W', 'X', 'SE', 'W', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'E', 'WN', 'E'],
            ['W', 'X', 'N', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'E', 'WS', 'X', 'X', 'X', 'E'],
            ['WE', 'SW', 'X', 'X', 'X', 'X', 'S', 'X', 'X', 'X', 'X', 'N', 'X', 'X', 'X', 'ES'],
            ['SW', 'N', 'X', 'X', 'X', 'E', 'NW', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'EN'],
            ['NW', 'X', 'X', 'X', 'X', 'S', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'E'],
            ['W', 'X', 'X', 'X', 'X', 'NE', 'W', 'S', 'S', 'X', 'S', 'X', 'X', 'ES', 'W', 'E'],
            ['W', 'X', 'X', 'X', 'X', 'X', 'E', 'NW', 'EN', 'W', 'EN', 'W', 'X', 'N', 'X', 'E'],
            ['W', 'X', 'X', 'S', 'X', 'X', 'E', 'WS', 'SE', 'W', 'X', 'X', 'X', 'X', 'S', 'E'],
            ['W', 'X', 'X', 'EN', 'W', 'X', 'X', 'N', 'N', 'X', 'X', 'X', 'X', 'E', 'NW', 'E'],
            ['W', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'E', 'SW', 'X', 'X', 'X', 'SE'],
            ['WE', 'WS', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'S', 'X', 'N', 'X', 'X', 'X', 'NE'],
            ['W', 'N', 'X', 'X', 'X', 'X', 'ES', 'W', 'X', 'NE', 'W', 'X', 'X', 'X', 'X', 'E'],
            ['WS', 'X', 'S', 'X', 'X', 'X', 'N', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'E'],
            ['WN', 'E', 'WN', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'SE', 'W', 'E'],
            ['WS', 'S', 'S', 'S', 'S', 'ES', 'WS', 'S', 'S', 'S', 'SE', 'SW', 'S', 'SN', 'S', 'SE'],
        ]
        robots = {
            'R': (2, 14),
            'G': (0, 3),
            'B': (11, 2),
            'Y': (2, 1)
        }
        target = (BLUE, (9, 12))
        return Game(grid=grid, robots=robots, target=target)

    def __init__(self, grid=None, robots=None, target=None):
        self.grid = grid
        self.robots = robots
        self.target = target
        self.moves = 0
        self.last = None

    def can_move(self, color, direction):
        if self.last == (color, REVERSE[direction]):
            return False
        x, y = self.robots[color]
        if direction in self.grid[y][x]:
            return False
        dx, dy = OFFSET[direction]
        new_pos = (x + dx, y + dy)
        if new_pos in self.robots.values():
            return False
        return True

    def compute_move(self, color, direction):
        x, y = self.robots[color]
        robots_positions = set(self.robots.values())
        dx, dy = OFFSET[direction]

        while True:
            if direction in self.grid[y][x]:
                break
            new_x, new_y = x + dx, y + dy
            if (new_x, new_y) in robots_positions:
                break
            x, y = new_x, new_y
        return (x, y)

    def do_move(self, color, direction):
        start = self.robots[color]
        if self.last == (color, REVERSE[direction]):
            raise Exception("Cannot move back immediately.")
        end = self.compute_move(color, direction)
        if start == end:
            raise Exception("Move didn't change position.")
        self.moves += 1
        self.robots[color] = end
        self.last = (color, direction)
        return (color, start, self.last)

    def undo_move(self, data):
        color, start, last = data
        self.moves -= 1
        self.robots[color] = start
        self.last = last

    def get_moves(self, colors=None):
        result = []
        colors = colors or COLORS
        for color in colors:
            for direction in DIRECTIONS:
                if self.can_move(color, direction):
                    result.append((color, direction))
        return result

    def over(self):
        color = self.target[0]
        return self.target[1] == self.robots[color]
