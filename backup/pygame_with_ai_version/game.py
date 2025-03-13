# Coordinate system follows Pygame's convention:
# - The first value (x) represents the horizontal coordinate.
# - The second value (y) represents the vertical coordinate.

import pygame
import sys
import ai
import consts

# Game settings
GRID_SIZE = 50  # Cell size
BOARD_SIZE = 16  # 16x16 board
UI_WIDTH = 250
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE + UI_WIDTH
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)


class RicochetRobotsGUI:
    """
    This GUI class renders the Ricochet Robots game and handles user input.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Ricochet Robots (Pygame)")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize the game
        self.game = RicochetRobotsGame.hard()
        self.selected_robot = None
        self.undo_stack = []

        # "AI Play" button
        self.ai_button_rect = pygame.Rect(
            BOARD_SIZE * GRID_SIZE + 10,
            420,
            100,
            40
        )

    def draw_grid(self):
        """Draw the board grid."""
        for x in range(0, BOARD_SIZE * GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, consts.RGB_LIGHT_GRAY, (x, 0), (x, BOARD_SIZE * GRID_SIZE))
        for y in range(0, BOARD_SIZE * GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, consts.RGB_LIGHT_GRAY, (0, y), (BOARD_SIZE * GRID_SIZE, y))

    def draw_walls(self):
        """Draw all walls on the board."""
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                cell = self.game.board[i][j]
                x, y = j * GRID_SIZE, i * GRID_SIZE
                wall_size = 5

                if consts.UP in cell:
                    pygame.draw.line(self.screen, consts.RGB_BLACK, (x, y), (x + GRID_SIZE, y), wall_size)
                if consts.RIGHT in cell:
                    pygame.draw.line(self.screen, consts.RGB_BLACK, (x + GRID_SIZE, y),
                                     (x + GRID_SIZE, y + GRID_SIZE), wall_size)
                if consts.DOWN in cell:
                    pygame.draw.line(self.screen, consts.RGB_BLACK, (x, y + GRID_SIZE),
                                     (x + GRID_SIZE, y + GRID_SIZE), wall_size)
                if consts.LEFT in cell:
                    pygame.draw.line(self.screen, consts.RGB_BLACK, (x, y), (x, y + GRID_SIZE), wall_size)

    def draw_target(self):
        """Draw the target on the board."""
        color = consts.COLOR_RGB_MAP.get(self.game.target[0])
        x, y = self.game.target[1][0] * GRID_SIZE, self.game.target[1][1] * GRID_SIZE
        if color is None:
            raise KeyError(f"key '{self.game.target[0]}' not found in COLOR_MAP")
        pygame.draw.rect(self.screen, color, (x + 15, y + 15, GRID_SIZE - 30, GRID_SIZE - 30))

    def draw_robots(self):
        """Draw all robots as circles."""
        for color, (rx, ry) in self.game.robots.items():
            x_pixel = rx * GRID_SIZE
            y_pixel = ry * GRID_SIZE

            # Draw the robot
            pygame.draw.circle(
                self.screen,
                consts.COLOR_RGB_MAP[color],
                (x_pixel + GRID_SIZE // 2, y_pixel + GRID_SIZE // 2),
                GRID_SIZE // 3
            )
            # Highlight the selected robot
            if self.selected_robot == color:
                pygame.draw.circle(
                    self.screen,
                    consts.RGB_BLACK,
                    (x_pixel + GRID_SIZE // 2, y_pixel + GRID_SIZE // 2),
                    GRID_SIZE // 3 + 5, 3
                )

    def draw_ai_button(self):
        """Draw the 'AI Play' button in the sidebar."""
        pygame.draw.rect(self.screen, consts.RGB_GRAY, self.ai_button_rect)
        font = pygame.font.SysFont(None, 28)
        text_surface = font.render("AI Play", True, consts.RGB_BLACK)
        text_rect = text_surface.get_rect(center=self.ai_button_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_sidebar(self):
        """Draw the sidebar with instructions, step count, and game status."""
        sidebar_x = BOARD_SIZE * GRID_SIZE
        pygame.draw.rect(self.screen, consts.RGB_DARK_GRAY, (sidebar_x, 0, UI_WIDTH, WINDOW_HEIGHT))

        font = pygame.font.SysFont(None, 28)
        text_lines = [
            "Controls:",
            "N - New Game",
            "U - Undo Move",
            "Arrow Keys - Move",
            "R/G/B/Y - Select Robot",
            "A - AI Play",  # Shortcut to let AI move
            "Esc - Quit",
            "",
            f"Selected: {self.selected_robot or 'None'}",
            f"Moves: {self.game.step_count}",
        ]

        # If the correct robot is at the target, show a win message
        if self.game.is_at_target():
            text_lines.append("You have won!")

        for i, line in enumerate(text_lines):
            text = font.render(line, True, consts.RGB_WHITE)
            self.screen.blit(text, (sidebar_x + 10, 20 + i * 30))

        # Draw the AI Play button
        self.draw_ai_button()

    def update_screen(self):
        """Refresh/redraw the entire game screen."""
        self.screen.fill(consts.RGB_WHITE)
        self.draw_grid()
        self.draw_walls()
        self.draw_target()
        self.draw_robots()
        self.draw_sidebar()
        pygame.display.flip()

    def handle_input(self):
        """Handle both keyboard and mouse inputs."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_n:  # Reset game
                    self.game = RicochetRobotsGame.hard()
                    self.undo_stack = []
                    self.selected_robot = None

                elif event.key == pygame.K_u:  # Undo last move
                    if self.undo_stack:
                        self.game.undo_move(self.undo_stack.pop())

                elif event.key in (pygame.K_r, pygame.K_g, pygame.K_b, pygame.K_y):
                    key_map = {
                        pygame.K_r: 'R',
                        pygame.K_g: 'G',
                        pygame.K_b: 'B',
                        pygame.K_y: 'Y'
                    }
                    self.selected_robot = key_map[event.key]

                elif event.key == pygame.K_a:
                    # The user pressed 'A' => let the AI play
                    self.ai_play()

                elif self.selected_robot:
                    direction_map = {
                        pygame.K_UP: consts.UP,
                        pygame.K_DOWN: consts.DOWN,
                        pygame.K_LEFT: consts.LEFT,
                        pygame.K_RIGHT: consts.RIGHT
                    }
                    if event.key in direction_map:
                        direction = direction_map[event.key]
                        try:
                            data = self.game.execute_move(self.selected_robot, direction)
                            self.undo_stack.append(data)
                        except Exception:
                            pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if user clicked the AI button
                if self.ai_button_rect.collidepoint(event.pos):
                    self.ai_play()

    # This method can be called by the "AI Play" button or by pressing 'A'.
    def ai_play(self):
        print("AI takes control")
        path = ai.play(self.game.get_current_state())  # path: [(robot_color, direction), (robot_color, direction), ...]
        for (robot_color, direction) in path:
            try:
                data = self.game.execute_move(robot_color, direction)
                self.undo_stack.append(data)
            except Exception as e:
                print(f"AI move error: {e}")
                break

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update_screen()
            self.clock.tick(10)

        pygame.quit()
        sys.exit()


class RicochetRobotsGame:
    """
    RicochetRobotsGame holds all game data (board, robots, target, etc.).
    """

    # ---------------------------- PUBLIC METHODS ----------------------------
    @staticmethod
    def hard():
        """ '_' represents a vacant place"""
        board_layout = (
            ('UL', 'U', 'U', 'U', 'UR', 'UL', 'U', 'U', 'U', 'RU', 'LU', 'U', 'U', 'U', 'UD', 'RU'),
            ('L', '_', 'DR', 'L', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'R', 'LU', 'R'),
            ('L', '_', 'U', '_', '_', '_', '_', '_', '_', '_', 'R', 'LD', '_', '_', '_', 'R'),
            ('LR', 'DL', '_', '_', '_', '_', 'D', '_', '_', '_', '_', 'U', '_', '_', '_', 'DR'),
            ('LD', 'U', '_', '_', '_', 'R', 'UL', '_', '_', '_', '_', '_', '_', '_', '_', 'UR'),
            ('LU', '_', '_', '_', '_', 'D', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'R'),
            ('L', '_', '_', '_', '_', 'UR', 'L', 'D', 'D', '_', 'D', '_', '_', 'RD', 'L', 'R'),
            ('L', '_', '_', '_', '_', '_', 'R', 'UL', 'RU', 'L', 'RU', 'L', '_', 'U', '_', 'R'),
            ('L', '_', '_', 'D', '_', '_', 'R', 'LD', 'DR', 'L', '_', '_', '_', '_', 'D', 'R'),
            ('L', '_', '_', 'RU', 'L', '_', '_', 'U', 'U', '_', '_', '_', '_', 'R', 'UL', 'R'),
            ('L', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'R', 'DL', '_', '_', '_', 'DR'),
            ('LR', 'LD', '_', '_', '_', '_', '_', '_', '_', 'D', '_', 'U', '_', '_', '_', 'UR'),
            ('L', 'U', '_', '_', '_', '_', 'RD', 'L', '_', 'UR', 'L', '_', '_', '_', '_', 'R'),
            ('LD', '_', 'D', '_', '_', '_', 'U', '_', '_', '_', '_', '_', '_', '_', '_', 'R'),
            ('LU', 'R', 'LU', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', 'DR', 'L', 'R'),
            ('LD', 'D', 'D', 'D', 'D', 'RD', 'LD', 'D', 'D', 'D', 'DR', 'DL', 'D', 'DU', 'D', 'DR'),
        )
        robots_positions = {
            consts.RED: (2, 14),
            consts.GREEN: (0, 3),
            consts.BLUE: (11, 2),
            consts.YELLOW: (2, 1)
        }
        target = (consts.BLUE, (9, 12))  # (target color, (x, y))

        return RicochetRobotsGame(board=board_layout, robots=robots_positions, target=target)

    def __init__(self, board=None, robots=None, target=None):
        self.board = board
        self.robots = robots
        self.target = target
        self.step_count = 0
        self.prev_move = None

    def get_current_state(self):
        """
        Returns the current game state:
          - board: a 2D list describing walls
          - robots: dict of robot_color -> (x,y)
          - target: (target_color, (x,y))
        """
        return {
            "board": self.board,
            "robots": dict(self.robots),
            "target": self.target
        }

    def execute_move(self, robot, movement):
        """
        Move the given robot in the specified direction until it
        is stopped by a wall or another robot.
        """
        start_pos = self.robots[robot]
        # Prevent immediate reversal of the same robot's move
        if self.prev_move == (robot, consts.OPPOSITE[movement]):
            raise Exception("Cannot move back immediately.")

        final_pos = self._compute_destination(robot, movement)
        if start_pos == final_pos:
            raise Exception("Move results in no change.")

        self.step_count += 1
        self.robots[robot] = final_pos
        self.prev_move = (robot, movement)
        return (robot, start_pos, self.prev_move)

    def undo_move(self, move_data):
        """Revert the last move."""
        robot, original_pos, previous = move_data
        self.step_count -= 1
        self.robots[robot] = original_pos
        self.prev_move = previous

    def available_moves(self, selection=None):
        """Return a list of all possible (robot, movement) moves."""
        moves = []
        selection = selection or consts.COLORS
        for robot in selection:
            for movement in consts.DIRECTIONS:
                if self._is_movable(robot, movement):
                    moves.append((robot, movement))
        return moves

    def is_at_target(self):
        """Check if the robot of target color occupies the target cell."""
        robot_color = self.target[0]
        return self.target[1] == self.robots[robot_color]

    # ---------------------------- INTERNAL METHODS ----------------------------

    def _is_movable(self, robot, movement):
        if self.prev_move == (robot, consts.OPPOSITE[movement]):
            return False
        x, y = self.robots[robot]
        if movement in self.board[y][x]:
            return False
        dx, dy = consts.DIRECTION_VECTORS[movement]
        next_position = (x + dx, y + dy)
        return next_position not in self.robots.values()

    def _compute_destination(self, robot, movement):
        x, y = self.robots[robot]
        occupied_positions = set(self.robots.values())
        dx, dy = consts.DIRECTION_VECTORS[movement]
        while True:
            # If there's a wall in this direction, stop.
            if movement in self.board[y][x]:
                break
            # Otherwise, look at the next spot
            next_x, next_y = x + dx, y + dy
            # If the next spot is occupied by a robot, stop.
            if (next_x, next_y) in occupied_positions:
                break
            x, y = next_x, next_y
        return (x, y)


# Run the game
if __name__ == "__main__":
    gui = RicochetRobotsGUI()
    gui.run()
