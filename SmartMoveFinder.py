import random
import ChessEngine

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
checkmate = 1000
stalemate = 0
depth_total = 2


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
        if gs.stalemate:
            opponent_max_score = stalemate
        elif gs.checkmate:
            opponent_max_score = -checkmate
        else:
            opponent_max_score = -checkmate
            for opponents_move in opponents_moves:
                gs.make_move(opponents_move)
                gs.get_valid_moves()
                if gs.checkmate:
                    score = checkmate
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
Helper method to make first recursive call
"""


def find_best_move_min_max(gs, valid_moves):
    global next_move
    next_moves = None
    # find_move_min_max(gs, valid_moves, depth_total, gs.white_to_move)
    find_move_negamax_alphabeta(
        gs,
        valid_moves,
        depth_total,
        -checkmate,
        checkmate,
        1 if gs.white_to_move else -1,
    )
    return next_move


def find_move_min_max(gs, valid_moves, depth, white_to_move):
    global next_moves
    if depth == 0:
        return score_material(gs.board)
    if white_to_move:
        max_score = -checkmate
        for move in valid_moves:
            gs.make_move(move)
            score = find_move_min_max(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == depth_total:
                    next_move = move
            gs.undo_move()
        return max_score
    else:
        min_score = checkmate
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == depth_total:
                    next_move = move
            gs.undo_move()
        return min_score


def find_move_negamax(gs, valid_moves, depth, turnmultiplier):
    global next_move
    if depth == 0:
        return turnmultiplier * score_board(gs)

    max_score = -checkmate
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax(gs, next_moves, depth - 1, -turnmultiplier)
        if score > max_score:
            max_score = score
            if depth == depth_total:
                next_move = move
        gs.undo_move()


def find_move_negamax_alphabeta(gs, valid_moves, depth, alpha, beta, turnmultiplier):
    global next_move
    if depth == 0:
        return turnmultiplier * score_board(gs)

    # Move ordering -
    max_score = -checkmate
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax_alphabeta(
            gs, next_moves, depth - 1, -beta, -alpha, -turnmultiplier
        )
        if score > max_score:
            max_score = score
            if depth == depth_total:
                next_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_board(gs):
    if gs.checkmate:
        if gs.white_to_move:
            return -checkmate
        else:
            return checkmate
    elif gs.stalemate:
        return stalemate
    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += piece_score[square[1]]
            elif square[0] == "b":
                score -= piece_score[square[1]]

    return score


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
