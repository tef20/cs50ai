"""
Tic Tac Toe Player: https://cs50.harvard.edu/ai/2020/projects/0/tictactoe

To improve, incorporate A-B Pruning. Currently explores full tree.
This might involve smarter use of data structures...

"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board, with X to start.
    """
    plays = 0

    # Count non-empty squares
    for i in range(3):
        for j in range(3):
            if board[i][j] != EMPTY:
                plays += 1

    # Even number of plays -> X's turn
    if plays % 2 == 0:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    available = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                available.add((i, j))

    return available


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Ensure manipulations of hypothetical board don't alter current board values
    possible_board = copy.deepcopy(board)
    current_player = player(possible_board)

    # Generate boards for all possible moves by current player
    if action in actions(possible_board):
        possible_board[action[0]][action[1]] = current_player
        return possible_board

    raise Exception("Invalid move.")


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check none empty horizontals
    for i in range(3):
        if board[i][0] and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

    # Check none empty verticals
    for j in range(3):
        if board[0][j] and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]

    # Check none empty L-R diagonal
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    # Check none empty R-L diagonal
    if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    # Is the board full?
    if not actions(board):
        return True

    # Is there a winner?
    if winner(board):
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_player = winner(board)

    # Did X win?
    if winning_player == X:
        return 1

    # Did O win?
    if winning_player == O:
        return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        return optimal_max(board)[0]
    else:
        return optimal_min(board)[0]


def optimal_max(board):
    """
    Returns (move, value) that maximises expected outcome value.
    """
    # Board full?
    if terminal(board):
        return [None, utility(board)]

    available_actions = list(actions(board))

    # Naive baseline comparison is negative infinity
    global_optimum = [None, -math.inf]

    # For each move, what would opponent do next? Update best move.
    for action in available_actions:
        # Anticipates optimal adversarial moves
        local_optimum = optimal_min(result(board, action))

        # Compares local vs global optima
        if global_optimum[1] <= local_optimum[1]:
            global_optimum = [action, local_optimum[1]]

    return global_optimum


def optimal_min(board):
    """
    Returns (move, value) that minimises expected outcome value.
    """
    if terminal(board):
        return [None, utility(board)]

    available_actions = list(actions(board))

    # Naive baseline comparison is positive infinity
    global_optimum = [None, math.inf]

    for action in available_actions:
        # Anticipates optimal adversarial moves.
        local_optimum = optimal_max(result(board, action))

        if global_optimum[1] >= local_optimum[1]:
            global_optimum = [action, local_optimum[1]]

    return global_optimum
