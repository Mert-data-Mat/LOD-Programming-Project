import pygame
import os
import json

# Initialize pygame
pygame.init()

# Dimensions and constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)

PIECE_IMAGES = {}

# Save and load game
def save_game(board, current_turn, file_name="chess_save.json"):
    """Save the current board state and turn to a file."""
    data = {
        "board": board,
        "current_turn": current_turn
    }
    with open(file_name, "w") as file:
        json.dump(data, file)
    print("Game saved successfully!")


def load_game(file_name="chess_save.json"):
    """Load the board state and turn from a file."""
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
            board = data["board"]
            current_turn = data["current_turn"]
            print("Game loaded successfully!")
            return board, current_turn
    except FileNotFoundError:
        print("Save file not found!")
        return None, None


# Load images
def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wQ", "wK", "bP", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        PIECE_IMAGES[piece] = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", f"{piece}.png")),
            (SQUARE_SIZE, SQUARE_SIZE)
        )


# Draw the chessboard and pieces
def draw_board(screen):
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(screen, board):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "--":
                screen.blit(PIECE_IMAGES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))


# Highlight moves
def highlight_square(screen, row, col):
    pygame.draw.rect(screen, HIGHLIGHT_COLOR, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlight_valid_moves(screen, moves):
    for row, col in moves:
        pygame.draw.circle(screen, HIGHLIGHT_COLOR,
                           (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                            row * SQUARE_SIZE + SQUARE_SIZE // 2),
                           SQUARE_SIZE // 5)


# Movement logic
def get_valid_moves(board, row, col):
    piece = board[row][col]
    if piece == "--":
        return []

    moves = []
    piece_type = piece[1]
    color = piece[0]

    if piece_type == "P":  # Pawn
        direction = -1 if color == "w" else 1
        if 0 <= row + direction < ROWS and board[row + direction][col] == "--":
            moves.append((row + direction, col))
            if (color == "w" and row == 6) or (color == "b" and row == 1):
                if board[row + 2 * direction][col] == "--":
                    moves.append((row + 2 * direction, col))
        for dcol in [-1, 1]:
            if 0 <= col + dcol < COLS and 0 <= row + direction < ROWS:
                target = board[row + direction][col + dcol]
                if target != "--" and target[0] != color:
                    moves.append((row + direction, col + dcol))

    elif piece_type == "R":  # Rook
        moves = get_straight_moves(board, row, col, color)

    elif piece_type == "B":  # Bishop
        moves = get_diagonal_moves(board, row, col, color)

    elif piece_type == "Q":  # Queen
        moves = get_straight_moves(board, row, col, color) + get_diagonal_moves(board, row, col, color)

    elif piece_type == "K":  # King
        for dr, dc in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                target = board[nr][nc]
                if target == "--" or target[0] != color:
                    moves.append((nr, nc))

    elif piece_type == "N":  # Knight
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                target = board[nr][nc]
                if target == "--" or target[0] != color:
                    moves.append((nr, nc))

    return moves


def get_straight_moves(board, row, col, color):
    moves = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        for step in range(1, ROWS):
            nr, nc = row + dr * step, col + dc * step
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                target = board[nr][nc]
                if target == "--":
                    moves.append((nr, nc))
                elif target[0] != color:
                    moves.append((nr, nc))
                    break
                else:
                    break
    return moves


def get_diagonal_moves(board, row, col, color):
    moves = []
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        for step in range(1, ROWS):
            nr, nc = row + dr * step, col + dc * step
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                target = board[nr][nc]
                if target == "--":
                    moves.append((nr, nc))
                elif target[0] != color:
                    moves.append((nr, nc))
                    break
                else:
                    break
    return moves


def is_in_check(board, color):
    king_pos = None
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == f"{color}K":
                king_pos = (row, col)
                break

    if not king_pos:
        return True  # King is missing, treat as checkmate

    opponent_color = "b" if color == "w" else "w"
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col][0] == opponent_color:
                moves = get_valid_moves(board, row, col)
                if king_pos in moves:
                    return True
    return False


def is_checkmate(board, color):
    if not is_in_check(board, color):
        return False

    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col][0] == color:
                moves = get_valid_moves(board, row, col)
                for move in moves:
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = temp_board[row][col]
                    temp_board[row][col] = "--"
                    if not is_in_check(temp_board, color):
                        return False
    return True


# Main game loop
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()

    load_images()

    board = [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    ]

    selected_square = None
    valid_moves = []
    current_turn = "w"

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // SQUARE_SIZE
                row = mouse_y // SQUARE_SIZE

                if selected_square:
                    if (row, col) in valid_moves:
                        start_row, start_col = selected_square
                        board[row][col] = board[start_row][start_col]
                        board[start_row][start_col] = "--"
                        current_turn = "b" if current_turn == "w" else "w"

                        if is_in_check(board, current_turn):
                            if is_checkmate(board, current_turn):
                                print(f"Checkmate! {current_turn.upper()} loses.")
                                running = False

                    selected_square = None
                    valid_moves = []
                else:
                    piece = board[row][col]
                    if piece[0] == current_turn:
                        selected_square = (row, col)
                        valid_moves = get_valid_moves(board, row, col)

        draw_board(screen)
        if selected_square:
            highlight_square(screen, *selected_square)
            highlight_valid_moves(screen, valid_moves)
        draw_pieces(screen, board)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()