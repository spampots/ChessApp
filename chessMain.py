import pygame as p
import os
import sys
import chessEngine
import moveAI

WIDTH = HEIGHT = 768
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGE = {}

def resource_path(relative_path):
    """Get absolute path to resource, works for development and for PyInstaller .exe."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def loadImage():
    """
    Loads images for all chess pieces and scales them to fit the board squares.
    The images are stored in the global IMAGE dictionary for easy access.
    """
    pieces = ['wp', 'bp', 'wR', 'bR', 'bK', 'wK', 'bB', 'wB', 'wQ', 'bQ', 'wN', 'bN']
    for piece in pieces:
        IMAGE[piece] = p.transform.scale(
            p.image.load(resource_path("images/" + piece + ".png")),
            (SQ_SIZE, SQ_SIZE)
        )

def showColorSelection(screen):
    """
    Displays a simple menu to choose a color for Player Versus Engine mode.
    Returns 'white' or 'black' based on the user's click.
    """
    font = p.font.SysFont("Arial", 32)
    color_choices = ["Play as White", "Play as Black"]
    chosen_color = None

    menu_bg = p.Surface(screen.get_size())
    menu_bg.fill(p.Color("white"))

    button_width = 300
    button_height = 60
    spacing = 20
    start_y = 250

    running_color_menu = True
    while running_color_menu:
        screen.blit(menu_bg, (0, 0))
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit(0)
            elif event.type == p.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, mode in enumerate(color_choices):
                    btn_x = (screen.get_width() // 2) - (button_width // 2)
                    btn_y = start_y + i * (button_height + spacing)
                    if (btn_x <= x <= btn_x + button_width) and (btn_y <= y <= btn_y + button_height):
                        chosen_color = "white" if i == 0 else "black"
                        running_color_menu = False

        # Draw color choice buttons
        for i, choice in enumerate(color_choices):
            btn_x = (screen.get_width() // 2) - (button_width // 2)
            btn_y = start_y + i * (button_height + spacing)
            button_rect = p.Rect(btn_x, btn_y, button_width, button_height)
            p.draw.rect(screen, p.Color("lightblue"), button_rect)
            label = font.render(choice, True, p.Color("black"))
            label_rect = label.get_rect(center=button_rect.center)
            screen.blit(label, label_rect)

        p.display.flip()

    return chosen_color

def showHomeScreen(screen):
    """
    Displays a home screen GUI with a big title and three buttons:
    Player Versus Player, Player Versus Engine, Engine Versus Engine.
    Returns the mode selected by the user as a string.
    """
    font_title = p.font.SysFont("Arial", 64, bold=True)
    font_buttons = p.font.SysFont("Arial", 36)

    home_bg = p.Surface(screen.get_size())
    home_bg.fill(p.Color("white"))

    title_text = "Chess"
    title_surface = font_title.render(title_text, True, p.Color("black"))
    title_rect = title_surface.get_rect(center=(WIDTH // 2, 100))

    modes = ["Player Versus Player", "Player Versus Engine", "Engine Versus Engine"]
    selected_mode = None

    button_width = 400
    button_height = 60
    spacing = 30
    start_y = 200

    running_home_screen = True
    while running_home_screen:
        screen.blit(home_bg, (0, 0))
        screen.blit(title_surface, title_rect)

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit(0)
            elif event.type == p.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i, mode in enumerate(modes):
                    btn_x = (screen.get_width() // 2) - (button_width // 2)
                    btn_y = start_y + i * (button_height + spacing)
                    if (btn_x <= x <= btn_x + button_width) and (btn_y <= y <= btn_y + button_height):
                        selected_mode = mode
                        running_home_screen = False

        # Draw buttons
        for i, mode in enumerate(modes):
            btn_x = (screen.get_width() // 2) - (button_width // 2)
            btn_y = start_y + i * (button_height + spacing)
            button_rect = p.Rect(btn_x, btn_y, button_width, button_height)
            p.draw.rect(screen, p.Color("lightblue"), button_rect)
            label = font_buttons.render(mode, True, p.Color("black"))
            label_rect = label.get_rect(center=button_rect.center)
            screen.blit(label, label_rect)

        p.display.flip()

    return selected_mode

def main():
    """
    Main function that initializes pygame, shows a home screen, and starts the chess game loop.
    """
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    # Show the home screen and get the selected game mode
    selected_mode = showHomeScreen(screen)

    # Determine playerOne and playerTwo based on user's selection
    if selected_mode == "Player Versus Player":
        playerOne = True
        playerTwo = True
    elif selected_mode == "Player Versus Engine":
        chosen_color = showColorSelection(screen)
        if chosen_color == "white":
            playerOne = True
            playerTwo = False
        else:  # chosen_color == "black"
            playerOne = False
            playerTwo = True
    else:  # Engine Versus Engine
        playerOne = False
        playerTwo = False

    gs = chessEngine.GameState()
    validMoves = gs.getValidMoves()
    loadImage()

    moveMade = False
    animate = False
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False

    while running:
        # Determine whose turn it is (human or AI)
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if move.isPawnPromotion:
                                    promoteTo = askForPromotion(screen, gs.whiteToMove)
                                    validMoves[i].promotionChoice = promoteTo
                                gs.makeMove(validMoves[i])
                                animate = True
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT:  # Undo last move
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r:     # Reset the board
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # Handle AI move if it is AI's turn
        if not gameOver and not humanTurn:
            AIMove = moveAI.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = moveAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        # If a move was made, update the valid moves list
        if moveMade:
            if animate:
                animateMove(gs.movelog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        # Check for checkmate or stalemate
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawEndGameText(screen, "Black wins by Checkmate")
            else:
                drawEndGameText(screen, "White wins by Checkmate")
        if gs.staleMate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

def askForPromotion(screen, isWhite):
    """
    Displays the promotion options when a pawn reaches the last rank.
    Returns the chosen piece notation as a string ('Q', 'R', 'B', 'N').
    """
    pieces = ['Q', 'R', 'B', 'N']
    pieceImages = [IMAGE[('w' if isWhite else 'b') + p] for p in pieces]
    optionWidth = WIDTH // 4
    rectHeight = HEIGHT // 3
    timeout = 5000  # 5 seconds
    start_time = p.time.get_ticks()

    while True:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                sys.exit(0)
            elif event.type == p.MOUSEBUTTONDOWN:
                x, y = event.pos
                idx = x // optionWidth
                if 0 <= idx < 4:
                    return pieces[idx]
        if p.time.get_ticks() - start_time > timeout:
            return 'Q'
        for i in range(4):
            rect = p.Rect(i * optionWidth, HEIGHT // 3, optionWidth, rectHeight)
            p.draw.rect(screen, p.Color("lightgray"), rect)
            screen.blit(pieceImages[i], rect)
        p.display.flip()

def drawBoard(screen):
    """
    Draws the chessboard with alternating squares (light, dark).
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    """
    Draws the chess pieces on the board according to their positions in 'board'.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGE[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected):
    """
    Highlights the selected square and valid moves from that square.
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            blueSurface = p.Surface((SQ_SIZE, SQ_SIZE))
            blueSurface.set_alpha(100)
            blueSurface.fill(p.Color('blue'))
            screen.blit(blueSurface, (c * SQ_SIZE, r * SQ_SIZE))

            yellowSurface = p.Surface((SQ_SIZE, SQ_SIZE))
            yellowSurface.set_alpha(100)
            yellowSurface.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(yellowSurface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected):
    """
    Draws the board, highlights squares, and draws pieces.
    """
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

def animateMove(move, screen, board, clock):
    """
    Animates a piece moving on the board from start to end squares.
    """
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frames = (abs(dR) + abs(dC)) * 10

    for frame in range(frames + 1):
        r = move.startRow + dR * frame / frames
        c = move.startCol + dC * frame / frames
        drawBoard(screen)
        drawPieces(screen, board)

        # Erase the piece from the ending square area
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnPassantMove:
                epRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow - 1)
                endSquare = p.Rect(move.endCol * SQ_SIZE, epRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGE[move.pieceCaptured], endSquare)

        screen.blit(IMAGE[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    """
    Displays the end-game text at the center of the screen.
    """
    font = p.font.SysFont("Helvetica", 48, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - textObject.get_width() / 2,
        HEIGHT / 2 - textObject.get_height() / 2
    )
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()
