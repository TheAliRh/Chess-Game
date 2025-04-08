import pygame as p
import Images
import ChessEngine
import SmartMoveFinder


width = height = 512
dimension = 8
sq_size = height // dimension
max_fps = 15
Images = {}


def load_images():
    pieces = ["wR", "wN", "wB", "wQ", "wK", "wp", "bR", "bN", "bB", "bQ", "bK", "bp"]
    for piece in pieces:
        Images[piece] = p.transform.scale(
            p.image.load("images/" + piece + ".png"), (sq_size, sq_size)
        )


def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False  # Flag variable for when a move is made
    animate = False  # Flag variable for when we should animate a move
    load_images()
    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False
    player_one = True
    player_two = False
    while running:
        human_turn = (gs.white_to_move and player_one) or (
            not gs.white_to_move and player_two
        )
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    col = location[0] // sq_size
                    row = location[1] // sq_size
                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(
                            player_clicks[0], player_clicks[1], gs.board
                        )
                        print(move.get_chess_notation())
                        if move in valid_moves:
                            gs.make_move(move)
                            move_made = True
                            animate = True
                            sq_selected = ()
                            player_clicks = []
                        else:
                            player_clicks = [sq_selected]
            # Key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False

                if e.key == p.K_r:  # Reset the game when 'r' is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

        # AI move finder
        if not game_over and not human_turn:
            ai_move = SmartMoveFinder.find_best_moves(gs, valid_moves)
            if ai_move is None:
                ai_move = SmartMoveFinder.find_random_moves(valid_moves)
            gs.make_move(ai_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animation_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False

        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, "Black wins by checkmate")
            else:
                draw_text(screen, "White wins by checkmate")
        elif gs.stalemate:
            game_over = True
            draw_text(screen, "Stalemate")

        draw_game_state(screen, gs, valid_moves, sq_selected)
        clock.tick(max_fps)
        p.display.flip()


"""
Highlight square selected and the possible moves of the piece on the selected square
"""


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == (
            "w" if gs.white_to_move else "b"
        ):  # Square selected is under piece which has turn to move
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100)  # Setting transparency (from 0 to 255)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * sq_size, r * sq_size))
            # Highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (sq_size * move.end_col, sq_size * move.end_row))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r + c) % 2)]
            p.draw.rect(
                screen, color, p.Rect(c * sq_size, r * sq_size, sq_size, sq_size)
            )


def draw_pieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "  ":
                screen.blit(
                    Images[piece], p.Rect(c * sq_size, r * sq_size, sq_size, sq_size)
                )


"""
Animating a move
"""


def animation_move(move, screen, board, clock):
    global colors
    coords = []  # List of coordinates that animation will move through
    dr = move.end_row - move.start_row
    dc = move.end_col - move.start_col
    frames_per_square = 10  # Frames to move one square
    frame_count = (abs(dr) + abs(dc)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = (
            move.start_row + dr * frame / frame_count,
            move.start_col + dc * frame / frame_count,
        )
        draw_board(screen)
        draw_pieces(screen, board)
        # Erase the piece move from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(
            move.end_col * sq_size, move.end_row * sq_size, sq_size, sq_size
        )
        p.draw.rect(screen, color, end_square)
        # Draw the captured piece onto rectangle
        if move.piece_captured != "  ":
            screen.blit(Images[move.piece_captured], end_square)
        # Draw moving piece
        screen.blit(
            Images[move.piece_moved],
            p.Rect(c * sq_size, r * sq_size, sq_size, sq_size),
        )
        p.display.flip()
        clock.tick(60)


def draw_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color("Red"))
    text_location = p.Rect(0, 0, width, height).move(
        width / 2 - text_object.get_width() / 2,
        height / 2 - text_object.get_height() / 2,
    )
    screen.blit(text_object, text_location)


if __name__ == "__main__":
    main()
