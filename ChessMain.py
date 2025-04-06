import pygame as p
import Images
import ChessEngine


Width = Height = 512
Dimension = 8
SQ_Size = Height // Dimension
Max_FPS = 15
Images = {}


def LoadImages():
    pieces = ["wR","wN","wB","wQ","wK","wp","bR","bN","bB","bQ","bK","bp"]
    for piece in pieces:
        Images[piece] = p.transform.scale(p.image.load("images/"+ piece +".png"), (SQ_Size, SQ_Size))
    

def main():
    p.init()
    screen = p.display.set_mode((Width, Height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validmoves = gs.get_valid_moves()
    movemade = False
    LoadImages()
    running = True
    sqSelected = ()
    PlayerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_Size
                row = location[1] // SQ_Size
                if sqSelected == (row, col):
                    sqSelected = ()
                    PlayerClicks = []
                else:
                    sqSelected = (row, col)
                    PlayerClicks.append(sqSelected)
                
                if len(PlayerClicks) == 2:
                    move = ChessEngine.Move(PlayerClicks[0], PlayerClicks[1], gs.board)
                    print(move.getchessnotation())
                    if move in validmoves:
                        gs.make_move(move)
                        movemade = True
                        sqSelected = ()
                        PlayerClicks = []
                    else:
                        PlayerClicks = [sqSelected]

            elif e.type == p.KEYDOWN: 
                if e.key == p.K_z:
                    gs.undomove()
                    movemade = True

        if movemade:
            validmoves = gs.get_valid_moves()
            movemade = False

        drawGameState(screen, gs)
        clock.tick(Max_FPS)
        p.display.flip()
    
    


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(Dimension):
        for c in range(Dimension):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_Size, r*SQ_Size, SQ_Size, SQ_Size))

def drawPieces(screen, board):
    for r in range(Dimension):
        for c in range(Dimension):
            piece = board[r][c]
            if piece != "  ":
                screen.blit(Images[piece], p.Rect(c*SQ_Size, r*SQ_Size, SQ_Size, SQ_Size))


if __name__ == "__main__":
    main()