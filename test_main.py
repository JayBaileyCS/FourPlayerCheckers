import unittest
import main


class MyTestCase(unittest.TestCase):

    def test_real_game_start(self):
        """Test creating a game, moving a piece, having the turn
        change, and then making a capture."""
        game = main.Game(1)
        assert (game.currentTurn() == 'p1')
        assert len(game.board.pieces) == 12 * 4
        assert game.board.pieces[(2, 4)].player == 'p1'
        game.movePiece([2, 4], [3, 3])
        assert (2, 4) not in game.board.pieces
        assert game.board.pieces[(3, 3)].player == 'p1'
        assert game.currentTurn() == 'p2'
        assert game.board.pieces[(4, 2)].player == 'p2'
        game.movePiece([4, 2], [2, 4])
        assert len(game.board.pieces) == 47

    def test_generating_game(self):
        checkers = main.Program(1)
        assert len(checkers.games) == 0
        assert checkers.max_id == 1

        game = checkers.newGame()
        assert len(checkers.games) == 1
        assert checkers.games[0].id == 0

        # Assert a second game is not started.
        game = checkers.newGame()
        assert game is None
        assert len(checkers.games) == 1

    def test_random_id_generation(self):
        checkers = main.Program(100)
        checkers.games = [{i: main.Game(i)} for i in range(100) if i != 57]
        assert len(checkers.games) == 99
        game = checkers.newGame()
        assert len(checkers.games) == 100
        assert game.id == 57

    def test_new_game(self):
        game = main.Game(1)
        self.assertEqual(game.id, 1)
        self.assertEqual(game.players, 4)
        self.assertEqual(game.turns, ['p1', 'p2', 'p3', 'p4'])
        self.assertEqual(game.current_turn, 'p1')
        assert(game.currentTurn() == 'p1')
        assert(game.checkWinner() is False)
        self.assertEqual(game.must_move_piece, None)
        assert len(game.board.pieces) == 12*4

    def test_change_turn(self):
        game = main.Game(1)
        expected_turns = ['p1', 'p2', 'p3', 'p4', 'p1']
        for i in range(len(expected_turns)):
            assert(game.currentTurn() == expected_turns[i])
            game.changeTurn()

    def test_change_turn_should_skip_player_with_no_pieces_remaining(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (4, 4): main.Piece('p4')}
        assert game.current_turn == 'p1'
        game.changeTurn()
        assert game.current_turn == 'p4'

    def test_check_winner_when_one_player_remains(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (4, 4): main.Piece('p1')}
        assert(game.checkWinner() is True)

    def test_check_winner_when_two_players_remain(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (4, 4): main.Piece('p2')}
        assert(game.checkWinner() is False)

    def test_valid_move(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (4, 4): main.Piece('p2')}
        assert game.movePiece((7, 7), (8, 8)) == "success"
        assert game.board.pieces[(8, 8)].player == 'p1'
        assert (7, 7) not in game.board.pieces
        assert game.current_turn == 'p2'

    def test_valid_capture(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p2'), (4, 4): main.Piece('p2')}
        assert game.movePiece((7, 7), (9, 9)) == "success"
        assert game.board.pieces[(9, 9)].player == 'p1'
        assert (8, 8) not in game.board.pieces
        assert game.current_turn == 'p2'

    def test_move_piece_from_empty_space(self):
        game = main.Game(1)
        game.board.pieces = {}
        assert game.movePiece((7, 7), (8, 8)) == "invalid move"

    def test_change_turn_only_on_valid_move(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (4, 4): main.Piece('p2')}
        assert game.movePiece((7, 7), (7, 8)) == "invalid move"
        assert game.current_turn == 'p1'
        assert game.movePiece((7, 7), (8, 8)) == "success"
        assert game.current_turn == 'p2'

    def test_move_piece_to_occupied_space(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p2')}
        assert game.movePiece((7, 7), (8, 8)) == "invalid move"

    def test_move_piece_to_unreachable_space(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1')}
        assert game.movePiece((7, 7), (7, 8)) == "invalid move"

    def test_move_piece_to_corner_space(self):
        game = main.Game(1)
        game.board.pieces = {(3, 3): main.Piece('p1')}
        assert game.movePiece((3, 3), (2, 2)) == "invalid move"

    def test_move_piece_off_board(self):
        game = main.Game(1)
        game.board.pieces = {(13, 10): main.Piece('p1')}
        assert game.movePiece((13, 10), (14, 11)) == "invalid move"

    def test_move_piece_when_must_move_another_piece(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p1')}
        game.must_move_piece = game.board.pieces[(8, 8)]
        assert game.movePiece((7, 7), (6, 6)) == "invalid move"

    def test_move_piece_when_must_capture_with_that_piece(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p2')}
        game.must_move_piece = game.board.pieces[(7, 7)]
        assert game.movePiece((7, 7), (9, 9)) == "success"

    def test_move_piece_when_must_capture_with_different_piece(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (5, 5): main.Piece('p2'), (4, 4): main.Piece('p1')}
        assert game.movePiece((7, 7), (8, 8)) == "invalid move"

    def test_move_piece_in_invalid_direction(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1')}
        assert game.movePiece((7, 7), (6, 6)) == "invalid move"

    def test_move_piece_in_invalid_direction_with_capture(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (6, 6): main.Piece('p2')}
        assert game.movePiece((7, 7), (5, 5)) == "invalid move"

    def test_move_king_in_otherwise_invalid_direction(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1')}
        game.board.pieces[(7, 7)].king = True
        assert game.movePiece((7, 7), (6, 6)) == "success"

    def test_move_king_in_otherwise_invalid_direction_with_capture(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (6, 6): main.Piece('p2')}
        game.board.pieces[(7, 7)].king = True
        assert game.movePiece((7, 7), (5, 5)) == "success"

    def test_attempt_to_capture_own_piece(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p1')}
        assert game.movePiece((7, 7), (9, 9)) == "invalid move"

    def test_attempt_to_perform_blocked_capture(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p2'), (9, 9): main.Piece('p2')}
        assert game.movePiece((7, 7), (9, 9)) == "invalid move"

    def test_should_promote_piece(self):
        game = main.Game(1)
        game.board.pieces = {(11, 7): main.Piece('p1')}
        game.movePiece((11, 7), (12, 8))
        assert game.board.pieces[(12, 8)].king is False
        game.current_turn = 'p1'
        game.movePiece((12, 8), (13, 7))
        assert game.board.pieces[(13, 7)].king is True
        game.current_turn = 'p1'
        assert game.movePiece((13, 7), (12, 8)) == "success"

    def test_should_not_switch_turn_on_multiple_captures(self):
        game = main.Game(1)
        game.board.pieces = {(7, 7): main.Piece('p1'), (8, 8): main.Piece('p2'), (10, 8): main.Piece('p2'), (4, 4): main.Piece('p2')}
        game.movePiece((7, 7), (9, 9))
        assert game.current_turn == 'p1'
        assert (8, 8) not in game.board.pieces
        game.movePiece((9, 9), (11, 7))
        assert game.current_turn == 'p2'
        assert (10, 8) not in game.board.pieces


if __name__ == '__main__':
    unittest.main()
