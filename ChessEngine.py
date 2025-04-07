import pygame as p


class GameState:

    def __init__(self):

        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]

        self.move_functions = {
            "p": self.get_pawn_moves,
            "R": self.get_rook_moves,
            "N": self.getknightmoves,
            "B": self.get_bishop_moves,
            "Q": self.get_queen_moves,
            "K": self.get_kings_move,
        }
        self.white_to_move = True
        self.move_log = []
        # Kings locations
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.check_mate = False
        self.stale_mate = False
        self.en_passant_possible = ()  # Square where en passant capture can happen
        # Castling rights
        self.white_castle_king_side = True
        self.white_castle_queen_side = True
        self.black_castle_king_side = True
        self.black_castle_queen_side = True
        self.castle_rights_log = [
            CastleRights(
                self.white_castle_king_side,
                self.black_castle_king_side,
                self.white_castle_queen_side,
                self.black_castle_queen_side,
            )
        ]

    """
    Make the move that is passed as a parameter
    """

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "  "
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # Move logging
        self.white_to_move = not self.white_to_move  # Switching turns
        # Update king's position
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        # If pawn moves twice, Next move can capture en passant
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = (
                (move.end_row + move.start_row) // 2,
                move.end_col,
            )
        else:
            self.en_passant_possible = ()
        # If en passant move, Must update the board to capture the pawn
        if move.en_passant:
            self.board[move.start_row][move.end_col] = "  "
        # If pawn promotion move happened, Change piece
        if move.pawn_promotion:
            promotioned_piece = input("Promote to Q, R, B or N:")
            self.board[move.end_row][move.end_col] = (
                move.piece_moved[0] + promotioned_piece
            )
        # Update castling rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(
            CastleRights(
                self.white_castle_king_side,
                self.black_castle_king_side,
                self.white_castle_queen_side,
                self.black_castle_queen_side,
            )
        )
        # Castle moves
        if move.castle:
            if move.end_col - move.start_col == 2:  # King side castling
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1
                ]  # Move the rook
                self.board[move.end_row][
                    move.end_col + 1
                ] = "  "  # Empty space where the rook was
            else:  # Queen side castling
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col + 1
                ]  # Move the rook
                self.board[move.end_row][
                    move.end_col - 2
                ] = "  "  # Empty space where the rook was

    """
    Undo the last move made
    """

    def undo_move(self):

        if len(self.move_log) != 0:

            move = self.move_log.pop()
            self.board[move.start_row][
                move.start_col
            ] = move.piece_moved  # Put piece on the starting square
            self.board[move.end_row][
                move.end_col
            ] = move.piece_captured  # Put back the captured piece
            self.white_to_move = not self.white_to_move  # Switching turns

        # Update king's position
        if move.piece_moved == "wK":

            self.white_king_location = (move.start_row, move.start_col)

        elif move.piece_moved == "bK":

            self.black_king_location = (move.start_row, move.start_col)

        # Undo en passant
        if move.en_passant:

            self.board[move.end_row][
                move.end_col
            ] = "  "  # Remove the pawn that was added in the wrong square
            self.board[move.start_row][
                move.end_col
            ] = (
                move.piece_captured
            )  # Puts the pawn back on the correct square it was captured from
            self.en_passant_possible = (
                move.end_row,
                move.end_col,
            )  # Allow an en passant to happen on the next move

        # Undo a 2 square pawn advance should make en_passant_possible = () again
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:

            self.en_passant_possible = ()

        # Give back castle rights if move took them away
        self.castle_rights_log.pop()  # Remove last moves updates
        CastleRights = self.castle_rights_log[-1]
        self.white_castle_king_side = CastleRights.wks
        self.black_castle_king_side = CastleRights.bks
        self.white_castle_queen_side = CastleRights.wqs
        self.black_castle_queen_side = CastleRights.bqs

        # Undo castle
        if move.castle:
            if move.end_col - move.start_col == 2:  # King side

                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 1
                ]  # Move the rook
                self.board[move.end_row][
                    move.end_col - 1
                ] = "  "  # Empty the space where the rook was

            else:  # Queen side
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][
                    move.end_col + 1
                ]  # Move the rook
                self.board[move.end_row][
                    move.end_col + 1
                ] = "  "  # Empty the space where the rook was

    """
    All moves with considering checks
    """

    def get_valid_moves(self):

        moves = []
        self.in_check, self.pins, self.checks = self.checking_pins_and_checks()

        if self.white_to_move:

            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]

        else:

            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        if self.in_check:

            if len(self.checks) == 1:  # Only 1 check, Block the check or move the king

                moves = self.get_all_possible_moves()
                # To block a check you must move a piece in between the enemy piece and the king
                check = self.checks[0]  # Check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][
                    check_col
                ]  # Enemy piece causing the check
                valid_squares = []  # Squares that pieces can move to

                # If knight , Must capture the knight or move the king, But other pieces can be blocked
                if piece_checking[1] == "N":

                    valid_squares = [(check_row, check_col)]

                else:

                    for i in range(1, 8):

                        valid_square = (
                            king_row + check[2] * i,
                            king_col + check[3] * i,
                        )  # Check[2] and check[3] are check directions
                        valid_squares.append(valid_square)

                        if (
                            valid_square[0] == check_row
                            and valid_square[1] == check_col
                        ):  # Once you get to piece end checks

                            break

                # Get ride of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # Going backwards when removing

                    if (
                        moves[i].piece_moved[1] != "K"
                    ):  # Move doesn't move the king so it must block check or capture piece

                        if (
                            not (moves[i].end_row, moves[i].end_col) in valid_squares
                        ):  # Moves doesn't block check or capture piece

                            moves.remove(moves[i])

            else:  # Double check, King has to move

                self.get_kings_move(king_row, king_col, moves)

        else:  # Not in check so all moves are fine

            moves = self.get_all_possible_moves()

        if len(moves) == 0:

            if self.in_check:  # Checking for check-mate

                self.check_mate = True

            else:  # Checking for stale-mate

                self.stale_mate = True

        else:

            self.check_mate = False
            self.stale_mate = False

        return moves

    """
    All moves without considering checks
    """

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.white_to_move) or (
                    turn == "b" and not self.white_to_move
                ):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)

        return moves

    """
    Pawn moves
    """

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:

            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = "b"

        else:

            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = "w"

        pawn_promotion = False

        if self.board[r + move_amount][c] == "  ":  # 1 square advance

            if not piece_pinned or pin_direction == (move_amount, 0):

                if (
                    r + move_amount == back_row
                ):  # If piece gets to back row then it's pawn promotion

                    pawn_promotion = True

                moves.append(
                    Move(
                        (r, c),
                        (r + move_amount, c),
                        self.board,
                        pawn_promotion=pawn_promotion,
                    )
                )

                if (
                    r == start_row and self.board[r + 2 * move_amount][c] == "  "
                ):  # 2 square advance

                    moves.append(Move((r, c), (r + 2 * move_amount, c), self.board))

        if c - 1 >= 0:  # Capture to left
            if not piece_pinned or pin_direction(move_amount, 1):

                if self.board[r + move_amount][c - 1][0] == enemy_color:

                    if r + move_amount == back_row:

                        pawn_promotion = True

                    moves.append(
                        Move(
                            (r, c),
                            (r + move_amount, c - 1),
                            self.board,
                            pawn_promotion=pawn_promotion,
                        )
                    )

                if (r + move_amount, c - 1) == self.en_passant_possible:

                    moves.append(
                        Move(
                            (r, c),
                            (r + move_amount, c - 1),
                            self.board,
                            en_passant=True,
                        )
                    )

        if c + 1 <= 7:  # Capture to right
            if not piece_pinned or pin_direction(move_amount, -1):

                if self.board[r + move_amount][c + 1][0] == enemy_color:

                    if r + move_amount == back_row:

                        pawn_promotion = True

                    moves.append(
                        Move(
                            (r, c),
                            (r + move_amount, c + 1),
                            self.board,
                            pawn_promotion=pawn_promotion,
                        )
                    )

                if (r + move_amount, c + 1) == self.en_passant_possible:

                    moves.append(
                        Move(
                            (r, c),
                            (r + move_amount, c + 1),
                            self.board,
                            en_passant=True,
                        )
                    )

    """
    Rook moves
    """

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemycolor = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if (
                        not piece_pinned
                        or pin_direction == d
                        or pin_direction == (-d[0], -d[1])
                    ):
                        endpiece = self.board[end_row][end_col]
                        if endpiece == "  ":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif endpiece[0] == enemycolor:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getknightmoves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knightmoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        allycolor = "w" if self.white_to_move else "b"
        for m in knightmoves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                if not piece_pinned:
                    endpiece = self.board[end_row][end_col]
                    if endpiece[0] != allycolor:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemycolor = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned:
                        endpiece = self.board[end_row][end_col]
                        if endpiece == "  ":
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif endpiece[0] == enemycolor:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)

    def get_kings_move(self, r, c, moves):
        kingmoves = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )
        allycolor = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + kingmoves[i][0]
            end_col = c + kingmoves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                endpiece = self.board[end_row][end_col]
                if endpiece[0] != allycolor:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def checking_pins_and_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemycolor = "b"
            allycolor = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemycolor = "w"
            allycolor = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        directions = (
            (-1, 0),
            (0, -1),
            (1, 0),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        )
        for j in range(len(directions)):
            d = directions[j]
            possiblepin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    endpiece = self.board[end_row][end_col]
                    if endpiece[0] == allycolor:
                        if possiblepin == ():
                            possiblepin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif endpiece[0] == enemycolor:
                        type = endpiece[1]
                        if (
                            (0 <= j <= 3 and type == "R")
                            or (4 <= j <= 7 and type == "B")
                            or (
                                i == 1
                                and type == "p"
                                and (
                                    (enemycolor == "w" and 6 <= j <= 7)
                                    or (enemycolor == "b" and 4 <= j <= 5)
                                )
                            )
                            or (type == "Q")
                            or (i == 1 and type == "K")
                        ):
                            if possiblepin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblepin)
                                break
                        else:
                            break
                else:
                    break
        knightmoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        for m in knightmoves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                endpiece = self.board[end_row][end_col]
                if endpiece[0] == enemycolor and endpiece[1] == "N":
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

    def update_castle_rights(self, move):
        pass


class CastleRights:

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    # Maps keys to values
    ranks_to_rows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {
        "h": 7,
        "g": 6,
        "f": 5,
        "e": 4,
        "d": 3,
        "c": 2,
        "b": 1,
        "a": 0,
    }
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(
        self,
        start_sq,
        end_sq,
        board,
        en_passant=False,
        pawn_promotion=False,
        castle=False,
    ):

        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.en_passant = en_passant
        self.pawn_promotion = pawn_promotion
        self.castle = castle

        if en_passant:

            self.piece_captured = (
                "bp" if self.piece_moved == "wp" else "wp"
            )  # En passant captures the opposite colored pawn

        self.move_id = (
            self.start_row * 1000
            + self.start_col * 100
            + self.end_row * 10
            + self.end_col
        )

    """
    Override the equals method
    """

    def __eq__(self, other):

        if isinstance(other, Move):

            return self.move_id == other.move_id

        return False

    def get_chess_notation(self):

        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(
            self.end_row, self.end_col
        )

    def get_rank_file(self, r, c):

        return self.cols_to_files[c] + self.rows_to_ranks[r]
