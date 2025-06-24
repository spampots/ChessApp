"""
This module implements the game state for a chess game, including the board setup,
move generation, special moves (pawn promotion, en passant, castling), and move logging.
"""

class GameState():
    def __init__(self):
        # Initialize the chess board as an 8x8 list.
        # Each element is a string representing color ('w' or 'b') and type of piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["--"] * 8,
            ["wp"] * 8,
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        
        # Map piece type to its move generation function.
        self.moveFunctions = {
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'K': self.getKingMoves,
            'Q': self.getQueenMoves,
            'B': self.getBishopMoves,
            'N': self.getKnightMoves
        }
        
        # True if it is White's turn; False for Black.
        self.whiteToMove = True
        
        # Log of moves made so far.
        self.movelog = []
        
        # Store the current king locations.
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        
        # Flags for checkmate and stalemate.
        self.checkMate = False
        self.staleMate = False
        
        # Track square available for en passant capture.
        self.enpassantPossible = ()
        
        # Initial castling rights.
        self.currentCastlingRights = CastlingRights(True, True, True, True)
        # Log of castling rights. We create a new deep copy so that later changes don't affect this log.
        self.CastleRightLog = [CastlingRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs
        )]

    def makeMove(self, move):
        """
        Makes the given move on the board.
        Performs pawn promotion, en passant captures, castling moves, updates king location,
        and logs the move.
        """
        # Empty the starting square.
        self.board[move.startRow][move.startCol] = "--"
        
        # Handle pawn promotion.
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionChoice
        else:
            self.board[move.endRow][move.endCol] = move.pieceMoved

        # En passant capture.
        if move.isEnPassantMove:
            if move.pieceMoved == "wp":
                self.board[move.endRow + 1][move.endCol] = "--"
            else:
                self.board[move.endRow - 1][move.endCol] = "--"

        # Handle castling move: move the rook accordingly.
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else:  # queenside castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = "--"

        # Log the move.
        self.movelog.append(move)
        
        # Switch turn.
        self.whiteToMove = not self.whiteToMove
        
        # Update king's location if the king is moved.
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Update the en passant square if a pawn advances two squares.
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enpassantPossible = ()

        # Update castling rights based on the move.
        self.updateCastleRights(move)
        
        # Append a deep copy of castling rights to the log.
        self.CastleRightLog.append(CastlingRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs
        ))

    def undoMove(self):
        """
        Undoes the last move made.
        Restores piece positions, en passant status, king location, and castling rights.
        """
        if len(self.movelog) != 0:
            # Pop the last move.
            move = self.movelog.pop()
            
            # Restore the moved piece to its starting square.
            self.board[move.startRow][move.startCol] = move.pieceMoved

            # Restore captured piece (or handle pawn promotion undo).
            if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceCaptured
            else:
                self.board[move.endRow][move.endCol] = move.pieceCaptured

            # Undo en passant move.
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                if move.pieceMoved == "wp":
                    self.board[move.endRow + 1][move.endCol] = "bp"
                else:
                    self.board[move.endRow - 1][move.endCol] = "wp"

            # If the move was a castling move, return the rook to its original square.
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside castle
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else:  # queenside castle
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"

            # Clear en passant possibility if it was set by a two-square pawn advance.
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # Switch turn back.
            self.whiteToMove = not self.whiteToMove
            
            # Restore king location if the king was moved.
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo castling rights: remove the last log entry and revert to a new copy of the previous state.
            self.CastleRightLog.pop()
            castleRights = self.CastleRightLog[-1]
            # Create a brand new object to avoid reference issues
            self.currentCastlingRights = CastlingRights(
                castleRights.wks,
                castleRights.bks, 
                castleRights.wqs, 
                castleRights.bqs
            )

    def updateCastleRights(self, move):
        """
        Updates castling rights based on the move.
        Revokes rights if the king or rook moves, or if a rook is captured from its original square.
        """
        # If king moves, remove both castling rights for that side
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        
        # If rook moves, remove corresponding castling right
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bks = False

        # Also update castling rights if a rook is captured from its original square.
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    def getValidMoves(self):
        """
        Returns a list of all valid moves by considering check conditions.
        Generates all possible moves (including castling), makes each move to test for check,
        and then undoes the move.
        """
        # Save the current state
        tempEnpassantPossible = self.enpassantPossible
        
        # Create a brand new copy of castling rights to avoid reference issues
        tempCastleRights = CastlingRights(
            self.currentCastlingRights.wks,
            self.currentCastlingRights.bks,
            self.currentCastlingRights.wqs,
            self.currentCastlingRights.bqs
        )
        
        # Generate all potential moves without checking for check
        moves = self.getAllPossibleMovees()

        # Check for castling possibilities
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # Filter out moves that leave own king in check
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        # Set game state flags
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        # Restore the saved state
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
        
        return moves

    def inCheck(self):
        """
        Determines if the current player is in check.
        """
        if self.whiteToMove:
            return self.SquareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.SquareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    def SquareUnderAttack(self, r, c):
        """
        Determines if the square (r, c) is attacked by any opponent piece.
        """
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMovees()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False        

    def getAllPossibleMovees(self):
        """
        Generates all potential moves for the current player without check detection.
        """
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        """
        Adds valid pawn moves from position (r, c) including forward moves,
        two-square advances from starting position, captures, and en passant.
        """
        if self.whiteToMove:
            # Single square advance.
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                # Two-square advance from starting row.
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # Capture left.
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
            # Capture right.
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))
        else:
            # Single square advance.
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                # Two-square advance from starting row.
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # Capture left.
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
            # Capture right.
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    def getRookMoves(self, r, c, moves):
        """
        Generates all rook moves from (r, c) in straight lines until blocked.
        """
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        enemy_color = 'b' if self.whiteToMove else 'w'
        
        for dr, dc in directions:
            temprow, tempcol = r + dr, c + dc
            while 0 <= temprow < 8 and 0 <= tempcol < 8:
                if self.board[temprow][tempcol][0] == self.board[r][c][0]:
                    break
                moves.append(Move((r, c), (temprow, tempcol), self.board))
                if self.board[temprow][tempcol][0] == enemy_color:
                    break
                temprow += dr
                tempcol += dc

    def getKnightMoves(self, r, c, moves):
        """
        Generates all knight moves from (r, c) in an "L" shape.
        """
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        
        ally_color = 'w' if self.whiteToMove else 'b'
        for dr, dc in offsets:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                if self.board[new_r][new_c][0] != ally_color:
                    moves.append(Move((r, c), (new_r, new_c), self.board))

    def getBishopMoves(self, r, c, moves):
        """
        Generates all diagonal moves for a bishop from (r, c) until blocked.
        """
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        enemy_color = 'b' if self.whiteToMove else 'w'
        
        for dr, dc in directions:
            temprow, tempcol = r + dr, c + dc
            while 0 <= temprow < 8 and 0 <= tempcol < 8:
                if self.board[temprow][tempcol][0] == self.board[r][c][0]:
                    break
                moves.append(Move((r, c), (temprow, tempcol), self.board))
                if self.board[temprow][tempcol][0] == enemy_color:
                    break
                temprow += dr
                tempcol += dc

    def getQueenMoves(self, r, c, moves):
        """
        Generates all queen moves by combining bishop and rook moves.
        """
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """
        Generates all king moves from (r, c), including one-square moves in any direction.
        """
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (-1, -1), (-1, 1), (1, -1)]
        ally_color = 'w' if self.whiteToMove else 'b'
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                if self.board[new_r][new_c][0] != ally_color:
                    moves.append(Move((r, c), (new_r, new_c), self.board))

    def getCastleMoves(self, r, c, moves):
        """
        Generates valid castling moves if the king is not in check
        and the path between king and rook is clear.
        """
        if self.SquareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.kingSideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.queenSideCastleMoves(r, c, moves)
    
    def kingSideCastleMoves(self, r, c, moves):
        """
        Generates kingside castling moves if the squares between king and rook are clear
        and not attacked.
        """
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.SquareUnderAttack(r, c+1) and not self.SquareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def queenSideCastleMoves(self, r, c, moves):
        """
        Generates queenside castling moves if the squares between king and rook are clear
        and not attacked.
        """
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            if not self.SquareUnderAttack(r, c-1) and not self.SquareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


class CastlingRights():
    def __init__(self, wks, bks, wqs, bqs):
        """
        Initializes castling rights.
        
        wks: White kingside castling available.
        bks: Black kingside castling available.
        wqs: White queenside castling available.
        bqs: Black queenside castling available.
        """
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    # Mappings between board ranks/files and indices.
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, promotionChoice=None, isEnPassantMove=False, isCastleMove=False):
        """
        Initializes a move.
        
        startSq: Starting square (row, col).
        endSq: Ending square (row, col).
        board: Current board state to retrieve piece information.
        promotionChoice: Desired piece for pawn promotion (default 'Q').
        isEnPassantMove: True if move is en passant.
        isCastleMove: True if move is castling.
        """
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "bp" if self.pieceMoved == "wp" else "wp"

        self.isPawnPromotion = (self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7))
        if self.isPawnPromotion and promotionChoice is not None:
            self.promotionChoice = promotionChoice
        else:
            self.promotionChoice = 'Q'

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        self.isCastleMove = isCastleMove

    def __eq__(self, other):
        """
        Overrides equality to compare moves by their unique moveID.
        """
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        """
        Returns a simple chess notation for the move.
        """
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        """
        Converts board coordinates to standard chess rank and file.
        """
        return self.colsToFiles[c] + self.rowsToRanks[r]