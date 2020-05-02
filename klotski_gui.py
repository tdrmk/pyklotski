import pygame

from game import Board, Position

TILE_SIZE = 100
WIDTH, HEIGHT = 4 * TILE_SIZE, 5 * TILE_SIZE
FPS = 60
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption('Klotski Puzzle')


def game():
    run = True
    board = Board.from_start_position()
    selected_piece = None

    def draw():
        win.fill((255, 255, 255))
        board.draw(win, TILE_SIZE)

    def handle_select(pos):
        nonlocal selected_piece
        selected_piece = None
        if 0 <= pos[0] < TILE_SIZE * 4 and 0 <= pos[1] < TILE_SIZE * 5:
            position = Position(pos[0] // TILE_SIZE, pos[1] // TILE_SIZE)
            selected_piece = board.get_piece(position)

    def reset():
        nonlocal board, selected_piece
        board = Board.from_start_position()
        selected_piece = None

    def handle_drop(pos):
        nonlocal selected_piece
        if 0 <= pos[0] < TILE_SIZE * 4 and 0 <= pos[1] < TILE_SIZE * 5:
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_select(event.pos)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                handle_drop(event.pos)

        clock.tick(FPS)


if __name__ == '__main__':
    game()
