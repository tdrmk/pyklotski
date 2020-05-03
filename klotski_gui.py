import pygame

from game import Board, Position
from utilities import darken_color

pygame.font.init()

TILE_SIZE = 100
main_font = pygame.font.SysFont('comicsans', 50)
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


def game():
    run = True
    board = Board.from_start_position()
    selected_piece = None

    # A surface to draw the board onto..
    board_surf = pygame.Surface(BOARD_SIZE)

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
            success_label = main_font.render(f"Congratulations!", 1, text_color)
            win.blit(success_label,
                     (BOARD_OFFSETS[0] + BOARD_SIZE[0] // 2 - success_label.get_width() // 2,
                      BOARD_OFFSETS[1] + BOARD_SIZE[1] // 2 - success_label.get_height() // 2))

    def handle_select(pos):
        nonlocal selected_piece
        selected_piece = None
        pos = pos[0] - BOARD_OFFSETS[0], pos[1] - BOARD_OFFSETS[1]
        if 0 <= pos[0] < BOARD_SIZE[0] and 0 <= pos[1] < BOARD_SIZE[1]:
            position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            selected_piece = board.get_piece(position)

    def reset():
        nonlocal board, selected_piece
        board = Board.from_start_position()
        selected_piece = None

    def handle_drop(pos):
        nonlocal selected_piece
        pos = pos[0] - BOARD_OFFSETS[0], pos[1] - BOARD_OFFSETS[1]
        if 0 <= pos[0] < BOARD_SIZE[0] and 0 <= pos[1] < BOARD_SIZE[1]:
            position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            if selected_piece:
                possible_pos = board.can_move(selected_piece, position)
                if possible_pos:
                    board.move(selected_piece, possible_pos)

    while run:
        draw()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                board.back()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                board.front()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_select(event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                handle_drop(event.pos)

        clock.tick(FPS)


if __name__ == '__main__':
    game()
