import pygame
import sys
from model import Game, NORTH, EAST, SOUTH, WEST

# from ricochet_model import GameBoard as Game

# Game settings
GRID_SIZE = 50  # Cell size
BOARD_SIZE = 16  # 16x16 board
UI_WIDTH = 250
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE + UI_WIDTH
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (178, 34, 34)
GREEN = (50, 205, 50)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (220, 220, 220)

COLOR_MAP = {'R': RED, 'G': GREEN, 'B': BLUE, 'Y': YELLOW}


class RicochetRobotsGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Ricochet Robots (Pygame)")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize the game
        self.game = Game.hardest()
        self.selected_robot = None
        self.undo_stack = []

    def draw_grid(self):
        """Draw the board grid"""
        for x in range(0, BOARD_SIZE * GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, LIGHT_GRAY, (x, 0), (x, BOARD_SIZE * GRID_SIZE))
        for y in range(0, BOARD_SIZE * GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, LIGHT_GRAY, (0, y), (BOARD_SIZE * GRID_SIZE, y))

    def draw_walls(self):
        """Draw walls on the board"""
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell = self.game.grid[i][j]
                x, y = j * GRID_SIZE, i * GRID_SIZE
                wall_size = 5

                if NORTH in cell:
                    pygame.draw.line(self.screen, BLACK, (x, y), (x + GRID_SIZE, y), wall_size)
                if EAST in cell:
                    pygame.draw.line(self.screen, BLACK, (x + GRID_SIZE, y), (x + GRID_SIZE, y + GRID_SIZE), wall_size)
                if SOUTH in cell:
                    pygame.draw.line(self.screen, BLACK, (x, y + GRID_SIZE), (x + GRID_SIZE, y + GRID_SIZE), wall_size)
                if WEST in cell:
                    pygame.draw.line(self.screen, BLACK, (x, y), (x, y + GRID_SIZE), wall_size)

    def draw_target(self):
        """Draw the target on the board"""
        color = COLOR_MAP.get(self.game.target[0])
        x, y = self.game.target[1][0] * GRID_SIZE, self.game.target[1][1] * GRID_SIZE
        if color == None:
            raise KeyError(f"key '{self.game.target[0]}' not found in COLOR_MAP")
        pygame.draw.rect(self.screen, color, (x + 15, y + 15, GRID_SIZE - 30, GRID_SIZE - 30))

    def draw_robots(self):
        """Draw all robots"""
        for color, (x, y) in self.game.robots.items():
            # Convert grid coordinates to pixel coordinates
            x_pixel = x * GRID_SIZE
            y_pixel = y * GRID_SIZE

            # Draw the robot as a circle
            pygame.draw.circle(self.screen, COLOR_MAP[color],
                               (x_pixel + GRID_SIZE // 2, y_pixel + GRID_SIZE // 2),
                               GRID_SIZE // 3)

            # Highlight the selected robot with an extra black border
            if self.selected_robot == color:
                pygame.draw.circle(self.screen, BLACK,
                                   (x_pixel + GRID_SIZE // 2, y_pixel + GRID_SIZE // 2),
                                   GRID_SIZE // 3 + 5, 3)

    def draw_sidebar(self):
        """Draw sidebar with instructions"""
        sidebar_x = BOARD_SIZE * GRID_SIZE
        pygame.draw.rect(self.screen, DARK_GRAY, (sidebar_x, 0, UI_WIDTH, WINDOW_HEIGHT))

        font = pygame.font.SysFont(None, 28)
        text_lines = [
            "Controls:",
            "N - New Game",
            "U - Undo Move",
            "Arrow Keys - Move",
            "R/G/B/Y - Select Robot",
            "Esc - Quit",
            "",
            f"Selected: {self.selected_robot or 'None'}"
        ]

        for i, line in enumerate(text_lines):
            text = font.render(line, True, WHITE)
            self.screen.blit(text, (sidebar_x + 10, 20 + i * 30))

    def update_screen(self):
        """Update the game screen"""
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_walls()
        self.draw_target()
        self.draw_robots()
        self.draw_sidebar()
        pygame.display.flip()

    def handle_input(self):
        """Handle user keyboard inputs"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_n:  # Reset game
                    self.game = Game.hardest()
                    self.undo_stack = []

                elif event.key == pygame.K_u:  # Undo last move
                    if self.undo_stack:
                        self.game.undo_move(self.undo_stack.pop())

                elif event.key in (pygame.K_r, pygame.K_g, pygame.K_b, pygame.K_y):
                    key_map = {pygame.K_r: 'R', pygame.K_g: 'G', pygame.K_b: 'B', pygame.K_y: 'Y'}
                    self.selected_robot = key_map[event.key]

                elif self.selected_robot:
                    direction_map = {
                        pygame.K_UP: NORTH,
                        pygame.K_DOWN: SOUTH,
                        pygame.K_LEFT: WEST,
                        pygame.K_RIGHT: EAST
                    }
                    if event.key in direction_map:
                        direction = direction_map[event.key]
                        try:
                            data = self.game.do_move(self.selected_robot, direction)
                            self.undo_stack.append(data)
                        except Exception:
                            pass

    def run(self):
        """Run the main game loop"""
        while self.running:
            self.handle_input()
            self.update_screen()
            self.clock.tick(10)

        pygame.quit()
        sys.exit()


# Run the game
if __name__ == "__main__":
    gui = RicochetRobotsGUI()
    gui.run()
