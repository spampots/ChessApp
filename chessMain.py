"""
This module implements the user interface for the chess game using pygame.
It displays the chessboard, renders pieces, and handles user interactions,
such as selecting squares, making moves, undoing moves, and handling pawn promotion.
"""

import pygame as p
import chessEngine

import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller .exe """
    try:
        base_path = sys._MEIPASS  # temporary folder PyInstaller extracts to
    except Exception:
        base_path = os.path.abspath(".")  # fallback for normal Python run
    return os.path.join(base_path, relative_path)

# Global constants for the UI
WIDTH = HEIGHT = 768               # Dimensions of the game window (square window)
DIMENSION = 8                      # Chessboard dimensions (8x8 grid)
SQ_SIZE = WIDTH // DIMENSION       # Size of each individual square on the chessboard
MAX_FPS = 15                       # Maximum frames per second for the game loop

# Dictionary to store scaled images of chess pieces
IMAGE = {}


def loadImage():
    """
    Loads images for all chess pieces and scales them to fit the board squares.
    The images are stored in the global IMAGE dictionary for easy access.
    """
    pieces = ['wp', 'bp', 'wR', 'bR', 'bK', 'wK', 'bB', 'wB', 'wQ', 'bQ', 'wN', 'bN']
    
    for piece in pieces:
        # Load the image and scale it to fit the size of a board square
        IMAGE[piece] = p.transform.scale(
            p.image.load(resource_path("images/" + piece + ".png")),
            (SQ_SIZE, SQ_SIZE)
        )


def main():
    """
    The main game loop.
    Initializes pygame, creates the game state, processes user events, and updates the pygame display.
    """
    # Initialize all pygame modules
    p.init()
    
    # Create the game window
    screen = p.display.set_mode((WIDTH, HEIGHT))
    
    # Setup a clock to control the frame rate
    clock = p.time.Clock()
    
    # Fill the screen with a white background
    screen.fill(p.Color("white"))
    
    # Create a game state object using the chess engine module
    gs = chessEngine.GameState()

    # Generate the initial set of valid moves
    validMoves = gs.getValidMoves()
    
    # Flag to determine if a move has been made, to update valid moves accordingly
    moveMade = False

    # Load the chess piece images
    loadImage()

    # Flag variable to control animation
    animate = False

    # Variables to track user interactions
    running = True                  # Game loop control flag
    sqSelected = ()                # Currently selected square (as a tuple: (row, col))
    playerClicks = []              # List to keep track of square clicks (e.g., [(6, 4), (4, 4)])

    # Variable to indicate if the game is over
    gameOver = False

    # Main game loop
    while running:
        # Process events from the pygame event queue
        for e in p.event.get():
            # Handle the quit event (closing the window)
            if e.type == p.QUIT:
                running = False

            # Handle mouse button clicks (square selection)
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  # Get the mouse click coordinates
                    col = location[0] // SQ_SIZE # Determine the column clicked
                    row = location[1] // SQ_SIZE # Determine the row clicked

                    # If the same square is clicked twice, reset the selection
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        # Track the selected square
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    # If two squares have been selected, attempt to make a move
                    if len(playerClicks) == 2:
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())  # Debug: Print move notation
                        for i in range(len(validMoves)):
                            # Check if the move is valid
                            if move == validMoves[i]:
                                # Handle pawn promotion
                                if move.isPawnPromotion:
                                    promoteTo = askForPromotion(screen, gs.whiteToMove)
                                    validMoves[i].promotionChoice = promoteTo
                                gs.makeMove(validMoves[i])
                                animate = True
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        # If move was invalid, retain the last selected square
                        if not moveMade:
                            playerClicks = [sqSelected]

            # Handle keyboard events (e.g., undo move, reset game)
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:  # Undo move
                    gs.undoMove()
                    moveMade = True
                    animate = False

                if e.key == p.K_r:  # Reset the board to the initial state
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False   
                    animate = False

        # If a move was made, update the valid moves for the new game state
        if moveMade:
            if animate:
                animateMove(gs.movelog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        # Draw the current game state on the board
        drawGameState(screen, gs, validMoves, sqSelected)
        
        # Check for game over conditions (checkmate or stalemate)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by Checkmate")
            else:
                drawText(screen, "White wins by Checkmate")
        if gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")
        
        # Limit the frame rate and update the display
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, validMoves, sqSelected):
    """
    Draws the current game state onto the display.

    Parameters:
        screen (pygame.Surface): The display surface where the game is drawn.
        gs (GameState): The current game state containing the board and move history.
    """
    drawBoard(screen)  # Draw the chessboard
    highlightSquares(screen, gs, validMoves, sqSelected)  # Highlight valid moves and selected squares
    drawPieces(screen, gs.board)  # Draw chess pieces on the board


def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Highlights the selected square and valid moves for the selected piece.

    Parameters:
        screen (pygame.Surface): The display surface where highlights are drawn.
        gs (GameState): The current game state object.
        validMoves (list): List of valid moves for the current game state.
        sqSelected (tuple): The currently selected square (row, col).
    """
    if sqSelected != ():
        r, c = sqSelected
        # Ensure the selected square contains a piece of the current player
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # Highlight the selected square in blue
            blueSurface = p.Surface((SQ_SIZE, SQ_SIZE))
            blueSurface.set_alpha(100)
            blueSurface.fill(p.Color('blue'))
            screen.blit(blueSurface, (c * SQ_SIZE, r * SQ_SIZE))

            # Highlight valid moves in yellow
            yellowSurface = p.Surface((SQ_SIZE, SQ_SIZE))
            yellowSurface.set_alpha(100)
            yellowSurface.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(yellowSurface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def askForPromotion(screen, isWhite):
    """
    Displays the promotion options for a pawn that reaches the end of the board.
    Waits for the user to click on one of the promotion piece options.

    Parameters:
        screen (pygame.Surface): The display surface for drawing promotion options.
        isWhite (bool): True if the current player is white, False if black.

    Returns:
        str: The chosen piece for promotion (e.g., 'Q', 'R', 'B', or 'N').
    """
    pieces = ['Q', 'R', 'B', 'N']
    pieceImages = [IMAGE[('w' if isWhite else 'b') + p] for p in pieces]
    optionWidth = WIDTH // 4       # Width of each promotion option box
    rectHeight = HEIGHT // 3       # Height of the promotion option area
    timeout = 5000  # 5 seconds timeout for promotion selection
    start_time = p.time.get_ticks()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:  # Handle quit event
                p.quit()
                quit()
            elif event.type == p.MOUSEBUTTONDOWN:
                x, y = event.pos
                idx = x // optionWidth  # Determine the clicked option
                if 0 <= idx < 4:
                    return pieces[idx]

        # Timeout fallback to default promotion (Queen)
        if p.time.get_ticks() - start_time > timeout:
            return 'Q'

        # Draw promotion options
        for i in range(4):
            rect = p.Rect(i * optionWidth, HEIGHT // 3, optionWidth, rectHeight)
            p.draw.rect(screen, p.Color("lightgray"), rect)
            screen.blit(pieceImages[i], rect)

        p.display.flip()


def drawBoard(screen):
    """
    Draws the chessboard on the display with alternating colors for squares.
    The top-left square is always light.

    Parameters:
        screen (pygame.Surface): The display surface for drawing the chessboard.
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]  # Light and dark square colors
    
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # Alternate colors based on row and column parity
            color = colors[(r + c) & 1]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    """
    Draws the chess pieces on the board at their current positions.

    Parameters:
        screen (pygame.Surface): The display surface for drawing pieces.
        board (list): The current 2D list representation of the board.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':  # Ensure the square is not empty
                screen.blit(IMAGE[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animateMove(move, screen, board, clock):
    """
    Animates a chess piece moving from its starting square to its destination square.

    Parameters:
        move (Move): The move object to animate.
        screen (pygame.Surface): The display surface for the animation.
        board (list): The current board state.
        clock (pygame.time.Clock): The clock to control animation frame rate.
    """
    global colors
    dR = move.endRow - move.startRow  # Difference in rows
    dC = move.endCol - move.startCol  # Difference in columns
    frameCount = (abs(dR) + abs(dC)) * 10  # Number of frames for the animation

    for frame in range(frameCount + 1):
        r = move.startRow + dR * frame / frameCount  # Interpolated row position
        c = move.startCol + dC * frame / frameCount  # Interpolated column position
        
        drawBoard(screen)  # Redraw the board
        drawPieces(screen, board)  # Redraw the pieces
        # Erase the piece from the ending square
        color = colors[(move.endRow + move.endCol) & 1]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':  # Redraw captured piece if any
            screen.blit(IMAGE[move.pieceCaptured], endSquare)
        screen.blit(IMAGE[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)  # Control frame rate


def drawText(screen, text):
    """
    Displays text (e.g., game-over messages) at the center of the screen.

    Parameters:
        screen (pygame.Surface): The display surface for drawing the text.
        text (str): The text message to display.
    """
    font = p.font.SysFont("Helvitica", 48, True, False)  # Font configuration
    textObject = font.render(text, 0, p.Color('Gray'))  # Render text with shadow
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - textObject.get_width() / 2,
        HEIGHT / 2 - textObject.get_height() / 2
    )
    # Draw shadow
    screen.blit(textObject, textLocation)
    # Draw main text
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()