#!/usr/bin/env python
from argparse import ArgumentParser

# Parsing command-line arguments
description = """
    Klotski Puzzle is yet another sliding block puzzle.
    How To Play:
        Drag the pieces to move it around the board.
        To win, move the largest piece to the bottom middle.
    Note: It takes at-least 81 steps to solve the puzzle.

    Use the arrow keys to undo or redo step(s).
    Press R to reset the board.
    Press A (or S) for computer solution.
    Press Q to quit.

    This application is implemented in python using PyGame module.
    To record the game, pass in --record argument.
"""
parser = ArgumentParser(description=description, epilog='Author: tdrk')
parser.add_argument('--record', default=False, action='store_true', help='record game screen')
parser.add_argument('--output', default='output.avi',
                    help='file to output recording. must have an .avi extension. default: output.avi ')
args = parser.parse_args()
RECORD_SCREEN = args.record
OUTPUT_FILE = args.output

import threading
from math import pi

import pygame

from game import Board, Position
from recorder import ScreenRecorder
from solver import bfs_solver
from utilities import darken_color

pygame.font.init()

TILE_SIZE = 100
main_font = pygame.font.Font(None, 50)
FONT_HEIGHT = main_font.get_height()
MARGIN = int(TILE_SIZE * 0.1)

# Window sizes
WIDTH, HEIGHT = 4 * TILE_SIZE + 2 * MARGIN, 5 * TILE_SIZE + 2 * MARGIN + 4 * FONT_HEIGHT

# Board positions
BOARD_OFFSETS = MARGIN, MARGIN + 2 * FONT_HEIGHT
BOARD_SIZE = 4 * TILE_SIZE, 5 * TILE_SIZE

# Score card positions
SCORE_OFFSETS = 0, HEIGHT - 2 * FONT_HEIGHT
SCORE_SIZE = WIDTH, 2 * FONT_HEIGHT

# Title positions
TITLE_OFFSETS = 0, 0
TITLE_SIZE = WIDTH, 2 * FONT_HEIGHT

FPS = 60
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Klotski Puzzle')


class AutoSolver:
    """
        Wrapper around the bfs_solver, maintains state useful for the game.
        Main States:
            enabled: When the solver is running
                - loading: When the solver is running and computing the steps async
                - otherwise, its simulating the steps
    """
    INTERVAL = int(FPS * 0.5)

    def __init__(self, board):
        self.board = board
        self.enabled = False  # whether auto-solver is running
        self.steps = None  # remaining steps to take

        # For computing the steps asynchronously
        # in another thread
        self.lock = threading.Lock()
        self.thread = None  # reference to the computation thread
        # NOTE: self.steps and self.thread is shared between threads, access needs a lock

        self.timer = 0  # just a counter to maintain an interval between steps

    @property
    def loading(self):
        # Checks if async thread is running
        with self.lock:
            return self.enabled and self.steps is None

    def enable(self, interval=INTERVAL):
        # To enable the auto-solver
        self.enabled = True
        self.timer = interval
        self.INTERVAL = interval

    def fetch_steps(self):
        # This method is called asynchronously
        # This is an CPU intensive blocking task.
        # updates the steps once computed.
        steps = bfs_solver(self.board)
        with self.lock:
            # modify shared variables after acquiring lock
            self.steps = steps
            self.thread = None

    def loop(self):
        # The main loop, to be called with every iteration of game loop
        # it modifies the board, when auto-solver is enabled.
        if self.enabled:
            with self.lock:
                # Steps not yet computed
                if self.steps is None:
                    # Compute the steps, asynchronously
                    if self.thread is None:
                        # launch a thread to compute the steps
                        self.thread = threading.Thread(target=self.fetch_steps)
                        self.thread.start()
                    # Computation is in progress

                # All the steps applied
                elif len(self.steps) == 0:
                    # Exit the auto-solver mode
                    self.steps = None
                    self.enabled = False

                # Adjust timer
                elif self.timer > 0:
                    # Timer to control the speed of solver
                    self.timer -= 1

                # Apply the steps after count-down
                else:
                    # MODIFIES THE BOARD!
                    piece, move = self.steps.pop(0)
                    self.board.move(piece, move)
                    # Reset the timer ..
                    self.timer = self.INTERVAL


class Loader:
    """
        Just a spinner to show while loading!
    """
    INCREMENT = 4 * pi / FPS

    def __init__(self):
        self.start_angle = 0
        self.end_angle = 3 * pi / 2

    def draw(self, surf, rect: pygame.Rect):
        """
            Pass in a surface and rect to draw the spinner on!
        """
        width = int(rect.width * 0.1)  # 10 % of width
        pygame.draw.arc(surf, (255, 255, 255), rect, self.start_angle, self.end_angle, width)

        # Update the angles
        self.start_angle = (self.start_angle - self.INCREMENT) % (2 * pi)
        self.end_angle = (self.end_angle - self.INCREMENT) % (2 * pi)


def game():
    # For screen-casting
    if RECORD_SCREEN:
        recorder = ScreenRecorder(WIDTH, HEIGHT, FPS, out_file=OUTPUT_FILE)
    run = True
    board = Board.from_start_position()
    solver = AutoSolver(board)
    selected_piece = None

    # A surface to draw the board onto..
    board_surf = pygame.Surface(BOARD_SIZE)
    loader = Loader()

    def draw():
        board_color = (205, 127, 50)
        text_background = (0, 100, 255)
        text_color = (255, 255, 255)
        # Fill the window and the board
        win.fill(darken_color(board_color, 0.5))
        board_surf.fill(board_color)

        # Draw the title label onto the window
        pygame.draw.rect(win, text_background, (TITLE_OFFSETS, TITLE_SIZE))
        title_label = main_font.render(f"KLOTSKI PUZZLE", 1, text_color)
        win.blit(title_label,
                 (TITLE_OFFSETS[0] + TITLE_SIZE[0] // 2 - title_label.get_width() // 2,
                  TITLE_OFFSETS[1] + TITLE_SIZE[1] // 2 - title_label.get_height() // 2))

        # Draw the steps label onto the window
        pygame.draw.rect(win, text_background, (SCORE_OFFSETS, SCORE_SIZE))
        steps_label = main_font.render(f"Step {board.number_of_steps}", 1, text_color)
        win.blit(steps_label,
                 (SCORE_OFFSETS[0] + SCORE_SIZE[0] // 2 - steps_label.get_width() // 2,
                  SCORE_OFFSETS[1] + SCORE_SIZE[1] // 2 - steps_label.get_height() // 2))

        # Draw the board and copy it onto the window
        board.draw(board_surf, TILE_SIZE)
        win.blit(board_surf, BOARD_OFFSETS)

        if board.is_solved:
            # Show the message when game is solved
            # NOTE: Game does not end when puzzle is solved, user can continue..
            success_label = main_font.render(f"Congratulations!", 1, text_color)
            win.blit(success_label,
                     (BOARD_OFFSETS[0] + BOARD_SIZE[0] // 2 - success_label.get_width() // 2,
                      BOARD_OFFSETS[1] + BOARD_SIZE[1] // 2 - success_label.get_height() // 2))

        if solver.loading:
            # Show a loader when auto-solver is computing the moves.
            loader.draw(win,
                        pygame.Rect((WIDTH // 2 - TILE_SIZE // 2, HEIGHT // 2 - TILE_SIZE // 2, TILE_SIZE, TILE_SIZE)))

    def handle_select(pos):
        # Handles mouse button down event.
        # Sets the selected_piece if a piece is selected
        nonlocal selected_piece
        selected_piece = None
        pos = pos[0] - BOARD_OFFSETS[0], pos[1] - BOARD_OFFSETS[1]
        if 0 <= pos[0] < BOARD_SIZE[0] and 0 <= pos[1] < BOARD_SIZE[1]:
            position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            selected_piece = board.get_piece(position)

    def handle_drop(pos):
        # Handles mouse button up event.
        # Moves the selected_piece if to specified position if allowed.
        # Specified position must be an empty position!
        nonlocal selected_piece
        pos = pos[0] - BOARD_OFFSETS[0], pos[1] - BOARD_OFFSETS[1]
        if 0 <= pos[0] < BOARD_SIZE[0] and 0 <= pos[1] < BOARD_SIZE[1]:
            click_position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            if selected_piece:
                possible_pos = board.can_move(selected_piece, click_position)
                if possible_pos:
                    board.move(selected_piece, possible_pos)

    def reset():
        # creates a new board to reset it
        nonlocal board, selected_piece, solver
        board = Board.from_start_position()
        selected_piece = None
        # Reset the solver as well
        solver = AutoSolver(board)

    def handle_user_event(_event):
        nonlocal selected_piece
        if _event.type == pygame.KEYDOWN:
            # Board reset
            if _event.key == pygame.K_r:
                reset()

            # History events
            if _event.key == pygame.K_LEFT:
                board.history_back()
            if _event.key == pygame.K_RIGHT:
                board.history_forward()

            # Solver
            if _event.key == pygame.K_a:  # Normal Solver
                selected_piece = None
                solver.enable()
            if _event.key == pygame.K_s:  # Fast solver
                selected_piece = None
                solver.enable(int(FPS * 0.1))

        if _event.type == pygame.MOUSEBUTTONDOWN and _event.button == 1:  # left click
            handle_select(_event.pos)

        if _event.type == pygame.MOUSEBUTTONUP and _event.button == 1:  # left click
            handle_drop(_event.pos)

    while run:
        draw()
        pygame.display.update()
        if RECORD_SCREEN:
            recorder.capture_frame(win)
        solver.loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                run = False

            if not solver.enabled:
                # User inputs taken only when solver not running
                handle_user_event(event)

        if not solver.enabled:
            # Power keys while navigating history
            # Allows continuous press
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                board.history_back()
            elif keys[pygame.K_UP]:
                board.history_forward()

        clock.tick(FPS)

    if RECORD_SCREEN:
        recorder.stop()
    pygame.quit()


if __name__ == '__main__':
    game()
