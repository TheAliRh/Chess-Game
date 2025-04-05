import pygame as p
import ChessEngine

class GameState():
    def __init__(self):
        
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["  ","  ","  ","  ","  ","  ","  ","  "],
            ["  ","  ","  ","  ","  ","  ","  ","  "],
            ["  ","  ","  ","  ","  ","  ","  ","  "],
            ["  ","  ","  ","  ","  ","  ","  ","  "],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]
            ]
        
        self.movefuncions = {'p': self.getpawnmoves, 'R': self.getrookmoves,
                              'N': self.getknightmoves, 'B': self.getbishopmoves,
                                'Q': self.getqueenmoves, 'K': self.getkingmoves}
        self.whiteToMove = True
        self.MoveLog = []
        self.whitekinglocation = (7, 4)
        self.blackkinglocation = (0, 4)
        self.incheck = False
        self.pins = []
        self.checks = []


    def makemove(self, move):
        self.board[move.startrow][move.startcol] = "  "
        self.board[move.endrow][move.endcol] = move.piecemoved
        self.MoveLog.append(move)
        self.whiteToMove = not self.whiteToMove


    def undomove(self):
        if len(self.MoveLog) != 0:
            move = self.MoveLog.pop()
            self.board[move.startrow][move.startcol] = move.piecemoved
            self.board[move.endrow][move.endcol] = move.piececaptured
            self.whiteToMove = not self.whiteToMove


    def getvalidmoves(self):
        moves = []
        self.incheck, self.pins, self.checks = self.checkforpinsandchecks()
        if self.whiteToMove:
            kingrow = self.whitekinglocation[0]
            kingcol = self.whitekinglocation[1]
        else:
            kingrow = self.blackkinglocation[0]
            kingcol = self.blackkinglocation[1] 
        if self.incheck:
            if len(self.checks) == 1:
                moves = self.getallpossiblemoves()
                check = self.checks[0]
                checkrow = check[0]
                checkcol = check[1]
                piecechecking = self.board[checkrow][checkcol]
                validsquares = []
                if piecechecking[1] == 'N':
                    validsquares = [(checkrow, checkcol)]
                else:
                    for i in range(1, 8):
                        validsquare = (kingrow + check[2] * i, kingcol + check[3] * i)
                        validsquares.append(validsquare)
                        if validsquare[0] == checkrow and validsquare[1] == checkcol:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piecemoved[1] != 'K':
                        if not (moves[i].endrow, moves[i].endcol) in validsquares:
                            moves.remove(moves[i])
            else:
                self.getkingmoves(kingrow, kingcol, moves)

        else:
            moves = self.getallpossiblemoves()


        return moves

    
    def getallpossiblemoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.movefuncions[piece](r, c, moves)

        return moves
                    

    def getpawnmoves(self, r, c, moves):
        piecepinned = False
        pindirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecepinned = True
                pindirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if self.board[r - 1][c] == "  ":
                if not piecepinned or pindirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == "  ":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    if not piecepinned or pindirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    if not piecepinned or pindirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            if self.board[r + 1][c] == "  ":
                if not piecepinned or pindirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == "  ":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piecepinned or pindirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piecepinned or pindirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))

    
    def getrookmoves(self, r, c, moves):
        piecepinned = False
        pindirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecepinned = True
                pindirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemycolor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:
                    if not piecepinned or pindirection == d or pindirection == (-d[0], -d[1]):
                        endpiece = self.board[endrow][endcol]
                        if endpiece == "  ":    
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                        elif endpiece[0] == enemycolor:
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                            break
                        else:
                            break
                else:
                    break


    def getknightmoves(self, r, c, moves):
        piecepinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecepinned = True
                self.pins.remove(self.pins[i])
                break
        knightmoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allycolor = 'w' if self.whiteToMove else 'b'
        for m in knightmoves:
            endrow = r + m[0]
            endcol = c + m[1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                if not piecepinned:
                    endpiece = self.board[endrow][endcol]
                    if endpiece[0] != allycolor:
                        moves.append(Move((r, c), (endrow, endcol), self.board))

    
    def getbishopmoves(self, r, c, moves):
        piecepinned = False
        pindirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecepinned = True
                pindirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemycolor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endrow = r + d[0] * i
                endcol = c + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:
                    if not piecepinned:
                        endpiece = self.board[endrow][endcol]
                        if endpiece == "  ":    
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                        elif endpiece[0] == enemycolor:
                            moves.append(Move((r, c), (endrow, endcol), self.board))
                            break
                        else:
                            break
                else:
                    break
    
 # -------------------------------------------------------------------------------------   
    def getqueenmoves(self, r, c, moves):
        self.getbishopmoves(r, c, moves)
        self.getrookmoves(r, c, moves)
    
    
    def getkingmoves(self, r, c, moves):
        kingmoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allycolor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endrow = r + kingmoves[i][0]
            endcol = c + kingmoves[i][1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] != allycolor:
                    moves.append(Move((r, c), (endrow, endcol), self.board))


    def checkforpinsandchecks(self):
        pins = []
        checks = []
        incheck = False
        if self.whiteToMove:
            enemycolor = 'b'
            allycolor = 'w'
            startrow = self.whitekinglocation[0]
            startcol = self.whitekinglocation[1]
        else:
            enemycolor = 'w'
            allycolor = 'b'
            startrow = self.blackkinglocation[0]
            startcol = self.blackkinglocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblepin = ()
            for i in range(1, 8):
                endrow = startrow + d[0] * i
                endcol = startcol + d[1] * i
                if 0 <= endrow < 8 and 0 <= endcol < 8:
                    endpiece = self.board[endrow][endcol]
                    if endpiece[0] == allycolor:
                        if possiblepin == ():
                            possiblepin = (endrow, endcol, d[0], d[1])
                        else:
                            break
                    elif endpiece[0] == enemycolor:
                        type = endpiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type  == 'p' and ((enemycolor == 'w' and 6 <= j <= 7) or (enemycolor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblepin == ():
                                incheck = True
                                checks.append((endrow, endcol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblepin)
                                break
                        else:
                            break
                else:
                    break
        knightmoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightmoves:
            endrow = startrow + m[0]
            endcol = startcol + m[1]
            if 0 <= endrow < 8 and 0 <= endcol < 8:
                endpiece = self.board[endrow][endcol]
                if endpiece[0] == enemycolor and endpiece[1] == 'N':
                    incheck = True
                    checks.append((endrow, endcol, m[0], m[1]))
        return incheck, pins, checks


class Move():
    rankstorows = {"1" : 7,"2" : 6,"3" : 5,"4" : 4,"5" : 3,"6" : 2,"7" : 1,"8" : 0,}
    rowstoranks = {v : k for k, v in rankstorows.items()}
    filestocols = {"h" : 7,"g" : 6,"f" : 5,"e" : 4,"d" : 3,"c" : 2,"b" : 1,"a" : 0,}
    colstofiles = {v : k for k, v in filestocols.items()}

    def __init__(self, startsq, endsq, board):
        self.startrow = startsq[0]
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.piecemoved = board[self.startrow][self.startcol]
        self.piececaptured = board[self.endrow][self.endcol]
        self.moveid = self.startrow * 1000 + self.startcol * 100 + self.endrow * 10 + self.endcol
        print(self.moveid)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveid == other.moveid
        return False

    
    def getchessnotation(self):
        return self.getrankfile(self.startrow, self.startcol) + self.getrankfile(self.endrow, self.endcol)


    def getrankfile(self, r, c):
        return self.colstofiles[c] + self.rowstoranks[r]
    
    