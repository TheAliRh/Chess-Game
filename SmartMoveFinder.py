import random
import ChessEngine

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
checkmate = 1000
stalemate = 0


gs = ChessEngine.GameState()

"""
Picks and returns a random move
"""


def find_random_moves(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


"""
Find the best move base on material alone
"""


def find_best_moves(gs, valid_moves):
    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_min_max_score = checkmate
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()

        opponent_max_score = -checkmate
        for opponents_move in opponents_moves:
            gs.make_move(opponents_move)
            if gs.checkmate:
                score = -turn_multiplier * checkmate
            elif gs.stalemate:
                score = stalemate
            else:
                score = -turn_multiplier * score_material(gs.board)
            if score > opponent_max_score:
                opponent_max_score = score

            gs.undo_move()
        if opponent_max_score < opponent_min_max_score:
            opponent_min_max_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move


"""
Score the board on material
"""


def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]

    return score
