from flask import Flask
from flask_cors import CORS
import random

DIRECTIONS = {'p1': 'down', 'p2': 'right', 'p3': 'up', 'p4': 'left'}
app = Flask(__name__)
CORS(app)


class Program:
    def __init__(self, max_id):
        self.games = []
        self.max_id = max_id


program = Program(1000)


class Game:
    def __init__(self, id):
        self.id = id
        self.board = Board()
        self.players = 4
        self.turns = [f"p{i}" for i in range(1, self.players + 1)]
        self.current_turn = 'p1'
        # If the user has previously captured a piece and still has a valid capture, they must capture again.
        self.must_move_piece = None

    def checkWinner(self):
        # Check if a player has won the game.
        players_remaining = []
        for piece in self.board.pieces.values():
            if piece.player not in players_remaining:
                players_remaining.append(piece.player)
        if len(players_remaining) == 1:
            print(players_remaining[0])
        else:
            print("false")
        return players_remaining[0] if len(players_remaining) == 1 else "false"

    def currentTurn(self):
        # Return the current player's turn.
        print(self.current_turn)
        return self.current_turn

    def movePiece(self, from_coords, to_coords):
        # Move a piece from one coordinate to another.
        from_coords, to_coords = tuple(from_coords), tuple(to_coords)
        if from_coords not in self.board.pieces:
            return "invalid move"
        if to_coords in self.board.pieces:
            return "invalid move"
        if not is_valid_square(to_coords, self.board):
            return "invalid move"
        if not is_reachable(from_coords, to_coords):
            return "invalid move"
        piece = self.board.pieces[from_coords]
        if piece.player != self.current_turn:
            return "invalid move"
        if self.must_move_piece is not None and piece != self.must_move_piece:
            return "invalid move"

        # If the piece is not capturing, check to see it is allowed to move in that direction
        # and that it has no valid captures.
        if not is_valid_direction(piece, from_coords, to_coords):
            return "invalid move"

        # Check to see how far the piece is moving - if it moves one space diagonally, it is not capturing.
        if abs(to_coords[0] - from_coords[0]) == 1 and abs(to_coords[1] - from_coords[1]) == 1:
            if can_capture_piece(self.current_turn, self.board):
                return "invalid move"
            if self.must_move_piece is not None and piece != self.must_move_piece:
                return "invalid move"
            self.board.pieces[to_coords] = piece
            del self.board.pieces[from_coords]

        else:
            """For captures, I have decided to only allow one capture at a time. While we could implement a pathfinding
            algorithm to allow for multiple captures, this would prevent fine-grained control - e.g, imagine a piece can
            capture up-left then up-right, or up-right then up-left, ending in the to_coord. We want the player to get to 
            choose which direction they start their capture.
            
            The fact that this allows us to avoid implementing a pathfinding algorithm is a nice bonus, but this
            is still the best path."""
            # TODO: Nice extra: Automatically perform follow-up captures if and only if there is only one valid capture.
            if is_valid_capture(piece, from_coords, to_coords, self.board):
                self.board.pieces[to_coords] = piece
                del self.board.pieces[from_coords]
                del self.board.pieces[get_captured_coords(from_coords, to_coords)]
                if can_capture_piece(self.current_turn, self.board, piece, to_coords):
                    self.must_move_piece = piece
                else:
                    self.must_move_piece = None  # Need to reset this if the piece cannot capture again.
            else:
                return "invalid move"

        if should_promote(piece, to_coords):
            piece.king = True
        self.changeTurn()
        self.board.board = self.board.generate_board()
        return self.board.board

    def changeTurn(self):
        # Change the current turn to the next player unless the player must make another capture.
        change = True
        players_remaining = []
        for piece in self.board.pieces.values():
            if piece.player not in players_remaining:
                players_remaining.append(piece.player)

        if not self.must_move_piece:
            while change:
                self.current_turn = self.turns[(self.turns.index(self.current_turn) + 1) % len(self.turns)]
                if self.current_turn in players_remaining:
                    change = False


class Board:
    def __init__(self):
        self.pieces = {}
        self.add_pieces(0, 3, 3, 11, True, 'p1')
        self.add_pieces(3, 0, 11, 3, True, 'p2')
        self.add_pieces(11, 3, 14, 11, False, 'p3')
        self.add_pieces(3, 11, 11, 14, False, 'p4')
        self.board = self.generate_board()

    def generate_board(self):
        board = [['.' for i in range(14)] for j in range(14)]
        # Add corners
        for i in range(3):
            for j in range(3):
                board[i][j] = 'X'
                board[i][j + len(board) - 3] = 'X'
                board[i + len(board) - 3][j] = 'X'
                board[i + len(board) - 3][j + len(board) - 3] = 'X'

        # Add pieces as 1, 2, 3, 4 based on player.
        for piece in self.pieces:
            board[piece[0]][piece[1]] = self.pieces[piece].player[1:]
        return board

    def add_pieces(self, start_i, start_j, finish_i, finish_j, skip_first, player):
        coords = [[i, j] for i in range(start_i, finish_i) for j in range(start_j, finish_j)]
        coords = [coords[i] for i in range(1 if skip_first else 0, len(coords), 2)]

        # Even numbered rows should be offset by 1. TODO: Improve this, if time.
        if int(player[-1]) % 2 == 1:
            for i, coord in enumerate(coords):
                if 4 <= i <= 7:
                    coords[i] = [coord[0], coord[1] + 1 if player == 'p3' else coord[1] - 1]

        for coord in coords:
            self.pieces[(coord[0], coord[1])] = Piece(player)

    # For testing purposes, if UI doesn't get done.
    def print_board(self):
        for row in self.board:
            print(' '.join(row))


class Piece:
    def __init__(self, player):
        self.player = player
        self.king = False


# Helper functions

def is_valid_square(to_coords, board):
    """Check to see if a square is on the board."""
    return 0 <= to_coords[0] < 14 and 0 <= to_coords[1] < 14 and board.board[to_coords[0]][to_coords[1]] != 'X'


def is_reachable(from_coords, to_coords):
    """Check to see if a move can be reached with diagonal moves."""
    if to_coords == from_coords:
        return False
    if (to_coords[0] + to_coords[1]) % 2 != (from_coords[0] + from_coords[1]) % 2:
        return False
    return True


def is_valid_direction(piece, from_coords, to_coords):
    """Check to see if a piece can be moved in that direction."""
    if piece.king:  # Kings can move in any direction.
        return True
    match DIRECTIONS[piece.player]:
        case 'down':
            return to_coords[0] > from_coords[0]
        case 'up':
            return to_coords[0] < from_coords[0]
        case 'left':
            return to_coords[1] < from_coords[1]
        case 'right':
            return to_coords[1] > from_coords[1]


def can_capture_piece(current_turn, board, specific_piece=None, specific_coords=None):
    """Check to see if a capturable piece exists for a player.
    If specific_piece is None, check for all pieces"""
    coords = []
    pieces = []
    if specific_piece is None:
        for coord, piece in board.pieces.items():
            if piece.player == current_turn:
                coords.append(coord)
                pieces.append(piece)
    else:
        coords = [specific_coords]
        pieces = [specific_piece]

    for i in range(len(pieces)):
        from_coords, piece = coords[i], pieces[i]
        adjacent_diagonal_coords = [(from_coords[0] + i, from_coords[1] + j) for i in [-1, 1] for j in [-1, 1]]
        adjacent_to_coords = [(from_coords[0] + i, from_coords[1] + j) for i in [-2, 2] for j in [-2, 2]]
        adjacent_diagonal_coords = [coord for coord in adjacent_diagonal_coords if
                                    is_valid_direction(piece, from_coords, coord)]
        adjacent_to_coords = [coord for coord in adjacent_to_coords if is_valid_direction(piece, from_coords, coord)]
        for j in range(len(adjacent_diagonal_coords)):
            coord, to_coord = adjacent_diagonal_coords[j], adjacent_to_coords[j]
            if is_valid_capture(piece, from_coords, to_coord, board):
                return True
    return False


def is_valid_capture(piece, from_coords, to_coords, board):
    """Check to see if a move is a valid capture."""
    if abs(to_coords[0] - from_coords[0]) != 2 or abs(to_coords[1] - from_coords[1]) != 2:
        return False
    if not is_valid_square(to_coords, board):  # If the square to move to is not on the board
        return False
    if to_coords in board.pieces:  # If the square to move to is blocked
        return False
    capture_coords = get_captured_coords(from_coords, to_coords)
    if capture_coords not in board.pieces or board.pieces[capture_coords].player == piece.player:
        return False
    return True


def get_captured_coords(from_coords, to_coords):
    """Get the coordinates of the captured piece."""
    return (from_coords[0] + to_coords[0]) // 2, (from_coords[1] + to_coords[1]) // 2


def should_promote(piece, coords):
    """Check to see if a piece should be promoted to a king.
    NOTE: There is some ambiguity in the rules about this.
    I'm assuming that a piece should be promoted if it reaches the opposite side of the board.
    Other possibilities could include reaching any edge, or counting the corners as edges."""
    if piece.king:
        return False
    if coords[0] == 13 and piece.player == 'p1':
        return True
    if coords[0] == 0 and piece.player == 'p3':
        return True
    if coords[1] == 13 and piece.player == 'p2':
        return True
    if coords[1] == 0 and piece.player == 'p4':
        return True
    return False


# Flask app functions

@app.route('/newGame', methods=['GET'])
def newGame():
    if len(program.games) == program.max_id:
        print("Maximum number of games reached.")
        return None
    # Create a new game, assigned to an ID that has not been used yet.
    game_ids = [game.id for game in program.games]
    id = random.choice([i for i in range(program.max_id) if i not in game_ids])
    program.games.append(Game(id))
    print(f"New game created with ID {id}.")
    print([game.id for game in program.games])
    return str(id)


@app.route('/getBoard/<game_id>', methods=['GET'])
def getBoard(game_id):
    # Return the board for a given game ID.
    if not game_id.isnumeric():
        print("invalid id")
        return "invalid id"
    game_id = int(game_id)

    for game in program.games:
        if game.id == game_id:
            return game.board.board
    print("invalid id")
    return "invalid id"


@app.route('/movePiece/<game_id>/<coords>', methods=['GET'])
# Should look like /movePiece/123/3,3,4,2 - moves (3, 3) to (4, 2).
def movePiece(game_id, coords):
    if not game_id.isnumeric():
        print("invalid id")
        return "invalid id"
    game_id = int(game_id)
    coords = coords.split(',')

    # All coords must be numeric
    if False in [coord.isnumeric() for coord in coords]:
        print("invalid coords")
        return "invalid coords"

    # Don't need to check for 0 <= coord <= 13 because that's done in is_valid_square
    coords = [int(coord) for coord in coords]
    from_coords, to_coords = coords[:2], coords[2:]
    # Move a piece from one coordinate to another.
    for game in program.games:
        if game.id == game_id:
            return game.movePiece(from_coords, to_coords)
    print("invalid id")
    return "invalid id"


@app.route('/checkWinner/<game_id>', methods=['GET'])
def checkWinner(game_id):
    # Check if a player has won the game.
    if not game_id.isnumeric():
        print("invalid id")
        return "invalid id"
    game_id = int(game_id)
    for game in program.games:
        if game.id == game_id:
            return game.checkWinner()
    print("invalid id")
    return "invalid id"


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
