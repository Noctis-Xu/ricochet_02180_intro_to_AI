import pygame
import sys
from src import consts, ai

# Desired delay (in milliseconds) between each AI move.
AI_MOVE_INTERVAL = 500

GRID_SIZE = 50
BOARD_SIZE = 16
UI_WIDTH = 250
WINDOW_WIDTH = BOARD_SIZE * GRID_SIZE + UI_WIDTH
WINDOW_HEIGHT = BOARD_SIZE * GRID_SIZE
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

KEY_MAP = {
    pygame.K_r: consts.RED,
    pygame.K_g: consts.GREEN,
    pygame.K_b: consts.BLUE,
    pygame.K_y: consts.YELLOW,
}

DIRECTION_MAP = {
    pygame.K_UP: consts.UP,
    pygame.K_DOWN: consts.DOWN,
    pygame.K_LEFT: consts.LEFT,
    pygame.K_RIGHT: consts.RIGHT
}


class RicochetRobotsGUI:
    """
    A GUI class that renders Ricochet Robots and handles both user and AI moves.
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Ricochet Robots (Pygame)")
        self.clock = pygame.time.Clock()
        self.running = True

        # The underlying game data
        self.game = RicochetRobotsGame.hard()
        self.undo_stack = []
        self.selected_robot = None

        # A button to trigger AI
        self.ai_button_rect = pygame.Rect(
            BOARD_SIZE * GRID_SIZE + 10,
            420,
            100,
            40
        )

        # AI state
        self.is_ai_active = False  # Whether AI is currently animating moves
        self.ai_moves_queue = []  # List of (robot_color, direction)
        self.ai_move_timer = 0  # Accumulator for time-based AI stepping
        self.ai_move_interval = AI_MOVE_INTERVAL  # Delay between AI moves (ms)

    def run(self):
        """
        Main loop of the game. We use time-based logic for the AI so that
        each move is executed with a delay (e.g. 500ms).
        """
        while self.running:
            dt = self.clock.tick(60)  # Get the time since last frame in ms
            self.handle_input()
            self._update_ai(dt)
            self.update_screen()
        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------------------
    #                           INPUT / AI LOGIC
    # -------------------------------------------------------------------------
    def handle_input(self):
        """
        Handle user keyboard/mouse input. If AI is active, you can choose
        to ignore the arrow keys, or let them happen in parallel.
        Here we demonstrate ignoring them if AI is active.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_n:
                    # Reset the game
                    self.game = RicochetRobotsGame.hard()
                    self.undo_stack.clear()
                    self.selected_robot = None
                    self.is_ai_active = False
                    self.ai_moves_queue.clear()

                elif event.key == pygame.K_u:
                    # Undo the last move
                    if self.undo_stack:
                        self.game.undo_move(self.undo_stack.pop())

                elif event.key in (pygame.K_r, pygame.K_g, pygame.K_b, pygame.K_y):
                    # Select robot
                    if not self.is_ai_active:
                        # Only allow user selection if AI not playing
                        self.selected_robot = KEY_MAP[event.key]

                elif event.key == pygame.K_a:
                    # Start AI
                    self.ai_play()

                elif self.selected_robot and not self.is_ai_active:
                    # Only allow arrow-key moves if AI is not active
                    if event.key in DIRECTION_MAP:
                        direction = DIRECTION_MAP[event.key]
                        try:
                            data = self.game.execute_move(self.selected_robot, direction)
                            self.undo_stack.append(data)
                        except Exception as ex:
                            print(f"User move error: {ex}")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check for clicking the AI button
                if self.ai_button_rect.collidepoint(event.pos):
                    self.ai_play()

    def ai_play(self):
        """
        Called when user presses 'A' or clicks the 'AI Play' button.
        We request a move sequence from the AI, then start the AI's
        step-by-step animation.
        """
        print("AI is activated!")
        # 1) Get the path from AI
        path = ai.play(self.game.get_current_state())  # list of (robot_color, direction)
        # 2) Clear old data (optional) or just extend
        self.ai_moves_queue.clear()
        # 3) Enqueue all AI moves
        self.ai_moves_queue.extend(path)
        # 4) Mark AI as active
        self.is_ai_active = True
        # 5) Reset the AI move timer
        self.ai_move_timer = 0

    def _update_ai(self, dt):
        """
        Called once per frame. This function checks if enough time has passed
        (ai_move_interval) to perform the next AI move in ai_moves_queue.

        :param dt: time in milliseconds since last frame
        """
        if not self.is_ai_active:
            return  # If AI not active, do nothing

        self.ai_move_timer += dt  # Accumulate time
        # If we have moves and enough time has passed, execute exactly one move
        if self.ai_moves_queue and self.ai_move_timer >= self.ai_move_interval:
            self.ai_move_timer -= self.ai_move_interval  # Reset or subtract interval

            robot_color, direction = self.ai_moves_queue.pop(0)
            try:
                data = self.game.execute_move(robot_color, direction)
                self.undo_stack.append(data)
            except Exception as ex:
                print(f"AI move error: {ex}")

        # If we've exhausted all moves, stop AI
        if not self.ai_moves_queue:
            self.is_ai_active = False
            print("AI has finished its path.")

    # -------------------------------------------------------------------------
    #                               DRAW LOGIC
    # -------------------------------------------------------------------------
    def update_screen(self):
        """Redraw everything each frame."""
        self.screen.fill(consts.RGB_WHITE)
        self.draw_grid()
        self.draw_walls()
        self.draw_target()
        self.draw_robots()
        self.draw_sidebar()
        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, BOARD_SIZE * GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, consts.RGB_LIGHT_GRAY, (x, 0), (x, BOARD_SIZE * GRID_SIZE))
        for y in range(0, BOARD_SIZE * GRID_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, consts.RGB_LIGHT_GRAY, (0, y), (BOARD_SIZE * GRID_SIZE, y))

    def draw_walls(self):
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
        color = consts.COLOR_RGB_MAP.get(self.game.target[0])
        tx, ty = self.game.target[1]
        x, y = tx * GRID_SIZE, ty * GRID_SIZE
        if color is None:
            raise KeyError(f"key '{self.game.target[0]}' not found in COLOR_MAP")
        pygame.draw.rect(self.screen, color, (x + 15, y + 15, GRID_SIZE - 30, GRID_SIZE - 30))

    def draw_robots(self):
        for color, (rx, ry) in self.game.robots.items():
            x_pixel = rx * GRID_SIZE
            y_pixel = ry * GRID_SIZE
            pygame.draw.circle(
                self.screen,
                consts.COLOR_RGB_MAP[color],
                (x_pixel + GRID_SIZE // 2, y_pixel + GRID_SIZE // 2),
                GRID_SIZE // 3
            )
            if self.selected_robot == color:
                pygame.draw.circle(
                    self.screen,
                    consts.RGB_BLACK,
                    (x_pixel + GRID_SIZE // 2, y_pixel + GRID_SIZE // 2),
                    GRID_SIZE // 3 + 5, 3
                )

    def draw_sidebar(self):
        sidebar_x = BOARD_SIZE * GRID_SIZE
        pygame.draw.rect(self.screen, consts.RGB_DARK_GRAY, (sidebar_x, 0, UI_WIDTH, WINDOW_HEIGHT))

        font = pygame.font.SysFont(None, 28)
        text_lines = [
            "Controls:",
            "N - New Game",
            "U - Undo Move",
            "Arrow Keys - Move",
            "R/G/B/Y - Select Robot",
            "A - AI Play",
            "Esc - Quit",
            "",
            f"Selected: {self.selected_robot or 'None'}",
            f"Moves: {self.game.step_count}"
        ]
        if self.game.is_at_target():
            text_lines.append("You have won!")

        # If AI is active, show some note (optional)
        if self.is_ai_active:
            text_lines.append("AI is running...")

        for i, line in enumerate(text_lines):
            text = font.render(line, True, consts.RGB_WHITE)
            self.screen.blit(text, (sidebar_x + 10, 20 + i * 30))

        self.draw_ai_button()

    def draw_ai_button(self):
        pygame.draw.rect(self.screen, consts.RGB_GRAY, self.ai_button_rect)
        font = pygame.font.SysFont(None, 28)
        text_surface = font.render("AI Play", True, consts.RGB_BLACK)
        text_rect = text_surface.get_rect(center=self.ai_button_rect.center)
        self.screen.blit(text_surface, text_rect)


class RicochetRobotsGame:
    """
    The class that holds board, robots, target, etc.
    """

    @staticmethod
    def hard():
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
        target = (consts.BLUE, (9, 12))
        return RicochetRobotsGame(board=board_layout, robots=robots_positions, target=target)

    def __init__(self, board=None, robots=None, target=None):
        self.board = board
        self.robots = robots
        self.target = target
        self.step_count = 0
        self.prev_move = None

    def get_current_state(self):
        return {
            "board": self.board,
            "robots": dict(self.robots),
            "target": self.target
        }

    def execute_move(self, robot, movement):
        start_pos = self.robots[robot]
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
        robot, original_pos, prev = move_data
        self.step_count -= 1
        self.robots[robot] = original_pos
        self.prev_move = prev

    def available_moves(self, selection=None):
        moves = []
        selection = selection or consts.COLORS
        for robot in selection:
            for movement in consts.DIRECTIONS:
                if self._is_movable(robot, movement):
                    moves.append((robot, movement))
        return moves

    def is_at_target(self):
        return self.target[1] == self.robots[self.target[0]]

    def _is_movable(self, robot, movement):
        if self.prev_move == (robot, consts.OPPOSITE[movement]):
            return False
        x, y = self.robots[robot]
        if movement in self.board[y][x]:
            return False
        dx, dy = consts.DIRECTION_VECTORS[movement]
        return (x + dx, y + dy) not in self.robots.values()

    def _compute_destination(self, robot, movement):
        x, y = self.robots[robot]
        occupied_positions = set(self.robots.values())
        dx, dy = consts.DIRECTION_VECTORS[movement]
        while True:
            if movement in self.board[y][x]:
                break
            next_x, next_y = x + dx, y + dy
            if (next_x, next_y) in occupied_positions:
                break
            x, y = next_x, next_y
        return (x, y)
