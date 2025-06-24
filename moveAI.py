import random

# Material values
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3.3, "N": 3, "p": 1}

# Piece-square tables
pawnScore = [
    [ 0, 0, 0, 0, 0, 0, 0, 0],
    [ 5, 5, 5, -5, -5, 5, 5, 5],
    [ 1, 1, 2, 3, 3, 2, 1, 1],
    [ 0, 0, 0, 2, 2, 0, 0, 0],
    [ 0, 0, 0, -2, -2, 0, 0, 0],
    [ 1, -1, -2, 0, 0, -2, -1, 1],
    [ 1, 2, 2, -2, -2, 2, 2, 1],
    [ 0, 0, 0, 0, 0, 0, 0, 0]
]

knightScore = [
    [-5, -4, -3, -3, -3, -3, -4, -5],
    [-4, -2, 0, 1, 1, 0, -2, -4],
    [-3, 1, 2, 3, 3, 2, 1, -3],
    [-3, 0, 3, 4, 4, 3, 0, -3],
    [-3, 1, 3, 4, 4, 3, 1, -3],
    [-3, 0, 2, 3, 3, 2, 0, -3],
    [-4, -2, 0, 0, 0, 0, -2, -4],
    [-5, -4, -3, -3, -3, -3, -4, -5]
]

bishopScore = [
    [-2, -1, -1, -1, -1, -1, -1, -2],
    [-1, 0, 0, 0, 0, 0, 0, -1],
    [-1, 0, 1, 1, 1, 1, 0, -1],
    [-1, 1, 1, 1, 1, 1, 1, -1],
    [-1, 0, 1, 1, 1, 1, 0, -1],
    [-1, 1, 1, 1, 1, 1, 1, -1],
    [-1, 1, 0, 0, 0, 0, 1, -1],
    [-2, -1, -1, -1, -1, -1, -1, -2]
]

rookScore = [
    [0, 0, 1, 2, 2, 1, 0, 0],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [-2, 0, 0, 0, 0, 0, 0, -2],
    [2, 2, 2, 2, 2, 2, 2, 2],
    [0, 0, 1, 2, 2, 1, 0, 0]
]

queenScore = [
    [-2, -1, -1, 0, 0, -1, -1, -2],
    [-1, 0, 0, 0, 0, 0, 0, -1],
    [-1, 0, 1, 1, 1, 1, 0, -1],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [-1, 1, 1, 1, 1, 1, 0, -1],
    [-1, 0, 1, 0, 0, 0, 0, -1],
    [-2, -1, -1, 0, 0, -1, -1, -2]
]

kingScore = [
    [-3, -4, -4, -5, -5, -4, -4, -3],
    [-3, -4, -4, -5, -5, -4, -4, -3],
    [-3, -4, -4, -5, -5, -4, -4, -3],
    [-3, -4, -4, -5, -5, -4, -4, -3],
    [-2, -3, -3, -4, -4, -3, -3, -2],
    [-1, -2, -2, -2, -2, -2, -2, -1],
    [2, 2, 0, 0, 0, 0, 2, 2],
    [2, 3, 1, 0, 0, 1, 3, 2]
]

piecePositionScores = {
    "p": pawnScore,
    "N": knightScore,
    "B": bishopScore,
    "R": rookScore,
    "Q": queenScore,
    "K": kingScore
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]

def findBestMoveNonrecursive(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None

    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentMoves = gs.getValidMoves()

        if gs.checkMate:
            score = CHECKMATE
        elif gs.staleMate:
            score = STALEMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                gs.getValidMoves()
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)

                if score > opponentMaxScore:
                    opponentMaxScore = score

                gs.undoMove()

            score = opponentMaxScore

        if score < opponentMinMaxScore:
            opponentMinMaxScore = score
            bestPlayerMove = playerMove

        gs.undoMove()

    return bestPlayerMove

def findBestMove(gs, validMoves):
    global nextMove, counter
    nextMove = None
    counter = 0
    # findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreBoard(gs)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore =  score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move 
            gs.undoMove()
        return minScore

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    #move ordering for alpha Beta Pruning -- implement later
    validMoves.sort(key=lambda move: -scoreMove(move, gs))


    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: #pruning out bad cses
            alpha = maxScore
        if alpha >= beta:
            break


    return maxScore



#score the board based on material
#a pos score is good to move for night

def scoreBoard(gs):
    if gs.checkMate:
        return -CHECKMATE if gs.whiteToMove else CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                pieceType = square[1]
                isWhite = square[0] == 'w'
                material = pieceScore[pieceType]
                positionScore = 0
                if pieceType in piecePositionScores:
                    posTable = piecePositionScores[pieceType]
                    positionScore = posTable[7 - row][col] if isWhite else posTable[row][col]
                total = material + 0.01 * positionScore
                score += total if isWhite else -total

    return score

# Material-only backup

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square != "--":
                value = pieceScore[square[1]]
                score += value if square[0] == 'w' else -value
    return score

def scoreMove(move, gs):
    score = 0
    if move.pieceCaptured != '--':
        # MVV-LVA: More valuable victim, less valuable attacker
        score += 10 * pieceScore[move.pieceCaptured[1]] - pieceScore[move.pieceMoved[1]]
    if move.pieceMoved[1] == 'p' and move.endRow in [0, 7]:
        score += 9  # promotion
    if move.pieceMoved[1] == 'p' and move.startCol != move.endCol:
        score += 2  # pawn capture
    return score
