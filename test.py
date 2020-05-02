from collections import namedtuple

Position = namedtuple('Position', ['x', 'y'])


def is_neighbour(_pos1, _pos2):
    return abs(_pos1.x - _pos2.x) + abs(_pos1.y - _pos2.y) == 1


class Piece:
    type = None

    def __init__(self, position):
        self.position = Position(*position)

    def positions(self):
        raise NotImplemented

    def __hash__(self):
        return hash((self.type, self.position))

    def can_move(self, empty_cells):
        raise NotImplemented

    @classmethod
    def move(cls, position):
        return cls(position)

    def __repr__(self):
        return f"{self.type}({self.position})"


class Piece1x1(Piece):
    type = 'Piece1x1'

    def positions(self):
        return [self.position]

    def can_move(self, empty_cells):
        moves = []
        neighbours = is_neighbour(*empty_cells)
        for empty_cell in empty_cells:
            if is_neighbour(self.position, empty_cell):
                if neighbours:
                    return list(empty_cells)
                moves.append(empty_cell)
        return moves


class Piece1x2(Piece):
    type = 'Piece1x2'

    def positions(self):
        return [self.position, Position(self.position.x, self.position.y + 1)]

    def can_move(self, empty_cells):
        moves = []
        x, y = self.position
        if Position(x, y - 1) in empty_cells:
            moves.append(Position(x, y - 1))
            if Position(x, y - 2) in empty_cells:
                moves.append(Position(x, y - 2))
        if Position(x, y + 2) in empty_cells:
            moves.append(Position(x, y + 1))
            if Position(x, y + 3) in empty_cells:
                moves.append(Position(x, y + 2))
        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_cells:
            moves.append(Position(x - 1, y))
        if {Position(x + 1, y), Position(x + 1, y + 1)} == empty_cells:
            moves.append(Position(x + 1, y))
        return moves


class Piece2x1(Piece):
    type = 'Piece2x1'

    def positions(self):
        return [self.position, Position(self.position.x + 1, self.position.y)]

    def can_move(self, empty_cells):
        moves = []
        x, y = self.position
        if Position(x - 1, y) in empty_cells:
            moves.append(Position(x - 1, y))
            if Position(x - 2, y) in empty_cells:
                moves.append(Position(x - 2, y))
        if Position(x + 2, y) in empty_cells:
            moves.append(Position(x + 1, y))
            if Position(x + 3, y) in empty_cells:
                moves.append(Position(x + 2, y))
        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_cells:
            moves.append(Position(x, y - 1))
        if {Position(x, y + 1), Position(x + 1, y + 1)} == empty_cells:
            moves.append(Position(x, y + 1))
        return moves


class Piece2x2(Piece):
    type = 'Piece2x2'

    def positions(self):
        return [self.position,
                Position(self.position.x + 1, self.position.y),
                Position(self.position.x, self.position.y + 1),
                Position(self.position.x + 1, self.position.y + 1)]

    def can_move(self, empty_cells):
        moves = []
        x, y = self.position
        if {Position(x, y - 1), Position(x + 1, y - 1)} == empty_cells:
            moves.append(Position(x, y - 1))
        if {Position(x, y + 2), Position(x + 1, y + 2)} == empty_cells:
            moves.append(Position(x, y + 1))
        if {Position(x - 1, y), Position(x - 1, y + 1)} == empty_cells:
            moves.append(Position(x - 1, y))
        if {Position(x + 2, y), Position(x + 2, y + 1)} == empty_cells:
            moves.append(Position(x + 1, y))
        return moves


class Board:
    def __init__(self, pieces):
        self.pieces = frozenset(pieces)

    def empty_cells(self):
        cells = {Position(x, y) for x in range(4) for y in range(5)}
        for piece in self.pieces:
            for pos in piece.positions():
                cells.remove(pos)
        return cells

    def moves(self):
        empty_cells = self.empty_cells()
        moves = []
        for piece in self.pieces:
            for position in piece.can_move(empty_cells):
                moves.append((piece, position))
        return moves

    @classmethod
    def initial_board(cls):
        return cls([Piece1x1((0, 4)), Piece1x1((1, 3)), Piece1x1((2, 3)), Piece1x1((3, 4)),
                    Piece1x2((0, 0)), Piece1x2((0, 2)), Piece1x2((3, 0)), Piece1x2((3, 2)),
                    Piece2x1((1, 2)),
                    Piece2x2((1, 0))])

    def main_piece(self):
        for piece in self.pieces:
            if piece.type == Piece2x2.type:
                return piece

    def is_solved(self):
        main_piece = self.main_piece()
        return main_piece.position == Position(1, 3)

    def on_move(self, piece, position):
        pieces = []
        for _piece in self.pieces:
            if _piece == piece:
                pieces.append(piece.move(position))
            else:
                pieces.append(_piece)
        return Board(pieces)

    def __hash__(self):
        return hash(self.pieces)

    def __eq__(self, other):
        return hash(self) == hash(other)


visited_boards = set()
new_boards = [Board.initial_board()]
iterations = {Board.initial_board(): 0}
transitions = {}
board = None

while new_boards:
    board = new_boards.pop(0)
    idx = iterations[board]
    if board.is_solved():
        print('Found:', idx)
        break
    visited_boards.add(board)
    for piece, move in board.moves():
        new_board = board.on_move(piece, move)
        if new_board not in visited_boards and new_board not in new_boards:
            iterations[new_board] = idx + 1
            new_boards.append(new_board)
            transitions[new_board] = (board, piece, move)

solution_board = board
steps = [board]
moves = []
while board != Board.initial_board():
    board, piece, move = transitions[board]
    steps.insert(0, board)
    moves.insert(0, (piece, move))
print(len(steps))
# print(len(visited_boards))
# solution_boards = []
# for board in visited_boards:
#     if board.is_solution():
#         solution_boards.append(board)

# print(len(solution_boards))
# print(min([iterations[board] for board in solution_boards]))
