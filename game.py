from collections import namedtuple

from utilities import draw_piece

Position = namedtuple('Position', ['x', 'y'])


def is_neighbour(_pos1: Position, _pos2: Position):
    # Manhattan distance is 1 then neighbour
    return abs(_pos1.x - _pos2.x) + abs(_pos1.y - _pos2.y) == 1


class Piece:
    COLOR = (193, 154, 107)
    WIDTH = 0
    HEIGHT = 0

    def __init__(self, x, y):
        self.position = Position(x, y)

    @property
    def positions(self):
        # returns the positions the piece occupies
        raise NotImplemented

    def update_position(self, position):
        # Could be used later for tracking ??
        self.position = position

    def possible_moves(self, empty_positions):
        # returns all positions the piece can move to.
        # empty_positions - set of empty positions
        # NOTE: USED BY SOLVER
        raise NotImplemented

    def possible_moves_ui(self, empty_positions):
        # same as above, however takes UI into consideration
        # return value is a tuple (ignore second value, as it is specific for UI)
        #  - first element is the list of all positions the piece can move
        #  - second element is a list corresponding to click positions
        #     which should result in new positions specified in the first element
        raise NotImplemented

    def draw(self, surf, size):
        draw_piece(surf, self.COLOR, self.position.x * size, self.position.y * size, self.WIDTH * size,
                   self.HEIGHT * size, size)


class Piece1x1(Piece):
    WIDTH = 1
    HEIGHT = 1

    @property
    def positions(self):
        yield self.position

    def possible_moves_ui(self, empty_positions):
        if is_neighbour(*empty_positions):
            # if empty positions are neighbouring each other and piece is neighbouring one of these positions
            # the piece can go to any of the empty positions
            if any(is_neighbour(self.position, empty_position) for empty_position in empty_positions):
                return list(empty_positions), [{empty_position} for empty_position in empty_positions]

        new_positions = []
        click_positions = []
        for empty_position in empty_positions:
            # if empty position is a neighbour of piece,
            # then it's possible position to move to
            if is_neighbour(self.position, empty_position):
                new_positions.append(empty_position)
                click_positions.append({empty_position})

        # positions where the UI is clicked is the same as new resultant positions
        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        if is_neighbour(*empty_positions):
            # if piece neighbours an empty position and empty positions themselves neighbour each other,
            # piece can move to any of the positions
            if any(is_neighbour(self.position, empty_position) for empty_position in empty_positions):
                return list(empty_positions)
            return []

        # if empty position is a neighbour, piece can move there.
        return [empty_position for empty_position in empty_positions if is_neighbour(self.position, empty_position)]


class Piece1x2(Piece):
    WIDTH = 1
    HEIGHT = 2

    @property
    def positions(self):
        yield self.position
        yield Position(self.position.x, self.position.y + 1)

    def possible_moves_ui(self, empty_positions):
        new_positions = []
        click_positions = []
        x, y = self.position
        if Position(x, y - 1) in empty_positions:
            # if movement possible towards top
            new_positions.append(Position(x, y - 1))
            click_positions.append({Position(x, y - 1)})

            if Position(x, y - 2) in empty_positions:
                new_positions.append(Position(x, y - 2))
                click_positions.append({Position(x, y - 2)})

        if Position(x, y + 2) in empty_positions:
            # if movement possible towards bottom
            new_positions.append(Position(x, y + 1))
            click_positions.append({Position(x, y + 2)})

            if Position(x, y + 3) in empty_positions:
                new_positions.append(Position(x, y + 2))
                click_positions.append({Position(x, y + 3)})

        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            # if movement possible towards left
            new_positions.append(Position(x - 1, y))
            click_positions.append(empty_positions)

        if {Position(x + 1, y), Position(x + 1, y + 1)} == empty_positions:
            # if movement possible towards right
            new_positions.append(Position(x + 1, y))
            click_positions.append(empty_positions)

        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        new_positions = []
        x, y = self.position
        if Position(x, y - 1) in empty_positions:
            new_positions.append(Position(x, y - 1))
            if Position(x, y - 2) in empty_positions:
                new_positions.append(Position(x, y - 2))
        if Position(x, y + 2) in empty_positions:
            new_positions.append(Position(x, y + 1))
            if Position(x, y + 3) in empty_positions:
                new_positions.append(Position(x, y + 2))

        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            new_positions.append(Position(x - 1, y))
        if {Position(x + 1, y), Position(x + 1, y + 1)} == empty_positions:
            new_positions.append(Position(x + 1, y))

        return new_positions


class Piece2x1(Piece):
    WIDTH = 2
    HEIGHT = 1

    @property
    def positions(self):
        yield self.position
        yield Position(self.position.x + 1, self.position.y)

    def possible_moves_ui(self, empty_positions):
        new_positions = []
        click_positions = []
        x, y = self.position
        if Position(x - 1, y) in empty_positions:
            # if movement possible towards left
            new_positions.append(Position(x - 1, y))
            click_positions.append({Position(x - 1, y)})

            if Position(x - 2, y) in empty_positions:
                new_positions.append(Position(x - 2, y))
                click_positions.append({Position(x - 2, y)})

        if Position(x + 2, y) in empty_positions:
            # if movement possible towards right
            new_positions.append(Position(x + 1, y))
            click_positions.append({Position(x + 2, y)})

            if Position(x + 3, y) in empty_positions:
                new_positions.append(Position(x + 2, y))
                click_positions.append({Position(x + 3, y)})

        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            # if movement possible towards top
            new_positions.append(Position(x, y - 1))
            click_positions.append(empty_positions)

        if {Position(x, y + 1), Position(x + 1, y + 1)} == empty_positions:
            # if movement possible towards bottom
            new_positions.append(Position(x, y + 1))
            click_positions.append(empty_positions)

        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        new_positions = []
        x, y = self.position
        if Position(x - 1, y) in empty_positions:
            new_positions.append(Position(x - 1, y))
            if Position(x - 2, y) in empty_positions:
                new_positions.append(Position(x - 2, y))
        if Position(x + 2, y) in empty_positions:
            new_positions.append(Position(x + 1, y))
            if Position(x + 3, y) in empty_positions:
                new_positions.append(Position(x + 2, y))

        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            new_positions.append(Position(x, y - 1))
        if {Position(x, y + 1), Position(x + 1, y + 1)} == empty_positions:
            new_positions.append(Position(x, y + 1))

        return new_positions


class Piece2x2(Piece):
    COLOR = (119, 17, 0)
    WIDTH = 2
    HEIGHT = 2

    @property
    def positions(self):
        yield self.position
        yield Position(self.position.x + 1, self.position.y)
        yield Position(self.position.x, self.position.y + 1)
        yield Position(self.position.x + 1, self.position.y + 1)

    def possible_moves_ui(self, empty_positions):
        new_positions = []
        click_positions = []
        x, y = self.position
        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            # if movement possible towards top
            new_positions.append(Position(x, y - 1))
            click_positions.append(empty_positions)

        if {Position(x, y + 2), Position(x + 1, y + 2)} == empty_positions:
            # if movement possible towards bottom
            new_positions.append(Position(x, y + 1))
            click_positions.append(empty_positions)

        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            # if movement possible towards left
            new_positions.append(Position(x - 1, y))
            click_positions.append(empty_positions)

        if {Position(x + 2, y), Position(x + 2, y + 1)} == empty_positions:
            # if movement possible towards right
            new_positions.append(Position(x + 1, y))
            click_positions.append(empty_positions)

        return new_positions, click_positions

    def possible_moves(self, empty_positions):
        new_positions = []
        x, y = self.position
        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_positions:
            new_positions.append(Position(x, y - 1))
        if {Position(x, y + 2), Position(x + 1, y + 2)} == empty_positions:
            new_positions.append(Position(x, y + 1))
        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_positions:
            new_positions.append(Position(x - 1, y))
        if {Position(x + 2, y), Position(x + 2, y + 1)} == empty_positions:
            new_positions.append(Position(x + 1, y))

        return new_positions


class Board:
    def __init__(self, pieces):
        # pieces is the list of pieces on the board,
        # with last piece being the main piece (expectation)
        assert isinstance(pieces[-1], Piece2x2)
        self.pieces = pieces
        self.main_piece = pieces[-1]
        self.history = []
        self.history_insert = 0

    @property
    def number_of_steps(self):
        return self.history_insert

    @classmethod
    def from_start_position(cls):
        return cls([Piece1x1(0, 4), Piece1x1(1, 3), Piece1x1(2, 3), Piece1x1(3, 4),
                    Piece1x2(0, 0), Piece1x2(0, 2), Piece1x2(3, 0), Piece1x2(3, 2),
                    Piece2x1(1, 2), Piece2x2(1, 0)])

    def empty_positions(self):
        # positions: initial store all positions on the board
        positions = {Position(x, y) for x in range(4) for y in range(5)}
        for piece in self.pieces:
            for occupied_position in piece.positions:
                # remove positions occupied by each of the pieces
                positions.remove(occupied_position)
        assert len(positions) == 2
        # positions with no piece are empty
        return positions

    @property
    def is_solved(self):
        # check if main piece is in the expected finish position
        return self.main_piece.position == Position(1, 3)

    def get_piece(self, position):
        # Gets the piece in the specified position
        for piece in self.pieces:
            if position in piece.positions:
                return piece
        return None

    def draw(self, surf, size):
        for piece in self.pieces:
            piece.draw(surf, size)

    def can_move(self, piece, click_position):
        empty_positions = self.empty_positions()
        possible_positions, click_positions = piece.possible_moves_ui(empty_positions)
        for possible_pos, click_pos in zip(possible_positions, click_positions):
            if click_position in click_pos:
                return possible_pos
        return None

    def _can_move(self, piece, position):
        empty_positions = self.empty_positions()
        possible_positions = piece.possible_moves(empty_positions)
        if position in possible_positions:
            return True

    def move(self, piece, position):
        assert self._can_move(piece, position)
        # insert into history the previous position
        self.history = self.history[:self.history_insert]
        self.history.append((piece, piece.position))
        self.history_insert += 1
        piece.update_position(position)

    def history_back(self):
        if self.history[:self.history_insert]:
            self.history_insert -= 1
            piece, position = self.history[self.history_insert]
            self.history[self.history_insert] = (piece, piece.position)
            piece.update_position(position)

    def history_forward(self):
        if self.history_insert < len(self.history):
            piece, position = self.history[self.history_insert]
            self.history[self.history_insert] = (piece, piece.position)
            self.history_insert += 1
            piece.update_position(position)
