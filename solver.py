"""
    Solves the klotski puzzle
"""

from game import Piece1x1 as _Piece1x1, Piece1x2 as _Piece1x2, Piece2x1 as _Piece2x1, Piece2x2 as _Piece2x2, \
    Board as _Board


class Piece1x1(_Piece1x1):
    def update_position(self, position):
        return Piece1x1(position.x, position.y)

    def __hash__(self):
        return hash(('PIECE1x1', self.position))

    @classmethod
    def from_piece(cls, piece):
        return cls(piece.position.x, piece.position.y)


class Piece1x2(_Piece1x2):
    def update_position(self, position):
        return Piece1x2(position.x, position.y)

    def __hash__(self):
        return hash(('PIECE1x2', self.position))

    @classmethod
    def from_piece(cls, piece):
        return cls(piece.position.x, piece.position.y)


class Piece2x1(_Piece2x1):
    def update_position(self, position):
        return Piece2x1(position.x, position.y)

    def __hash__(self):
        return hash(('PIECE2x1', self.position))

    @classmethod
    def from_piece(cls, piece):
        return cls(piece.position.x, piece.position.y)


class Piece2x2(_Piece2x2):
    def update_position(self, position):
        return Piece2x2(position.x, position.y)

    def __hash__(self):
        return hash(('PIECE2x2', self.position))

    @classmethod
    def from_piece(cls, piece):
        return cls(piece.position.x, piece.position.y)


class Board(_Board):
    def move(self, piece, position):
        pieces = tuple(
            _piece if _piece != piece
            else piece.update_position(position)
            for _piece in self.pieces
        )
        return Board.from_pieces(pieces)

    def potential_moves(self):
        moves = []
        empty_positions = self.empty_positions()
        for piece in self.pieces:
            for position in piece.possible_moves(empty_positions):
                moves.append((piece, position))
        return moves

    def __hash__(self):
        return hash(frozenset(self.pieces))

    def __eq__(self, other):
        return hash(self) == hash(other)

    @classmethod
    def from_pieces(cls, pieces: tuple):
        return cls(pieces)

    @classmethod
    def from_board(cls, _board: _Board):
        pieces = []
        for piece in _board.pieces:
            if isinstance(piece, _Piece1x1):
                pieces.append(Piece1x1.from_piece(piece))
            elif isinstance(piece, _Piece1x2):
                pieces.append(Piece1x2.from_piece(piece))
            elif isinstance(piece, _Piece2x1):
                pieces.append(Piece2x1.from_piece(piece))
            elif isinstance(piece, _Piece2x2):
                pieces.append(Piece2x2.from_piece(piece))
            else:
                raise NotImplemented
        return cls.from_pieces(tuple(pieces))

    def map_piece(self, piece, _board: _Board):
        # Returns the corresponding piece in _board O(1)
        return _board.pieces[self.pieces.index(piece)]


def bfs_solver(_board: _Board):
    start_board = Board.from_board(_board)
    # BFS Algorithm to find shortest route to solution
    visited_boards = set()

    # list maintains bfs order, set is O(log n) search
    new_boards = [start_board]
    new_boards_set = {start_board}
    transitions = {}
    board = None
    while new_boards:
        # explore the first element of the list
        board = new_boards.pop(0)  # O(1)
        new_boards_set.remove(board)  # O(log n)

        if board.is_solved:
            # Found the solution
            break

        # mark as visited
        visited_boards.add(board)
        for piece, move in board.potential_moves():
            # go to new board to explore it.
            new_board = board.move(piece, move)
            if new_board not in visited_boards and \
                    new_board not in new_boards_set:  # O(log n)
                new_boards.append(new_board)  # to maintain order
                new_boards_set.add(new_board)  # for searching

                # Apply move to piece in board to go to new_board
                # NOTE: Also map to piece in the _board, as pieces in Board as immutable,
                # while _Board maintains same set of pieces.
                transitions[new_board] = (board, board.map_piece(piece, _board), move)

    # The obtained solution
    # solution_board = board
    moves_taken = []
    while board != start_board:
        board, piece, move = transitions[board]
        moves_taken.insert(0, (piece, move))
    return moves_taken
