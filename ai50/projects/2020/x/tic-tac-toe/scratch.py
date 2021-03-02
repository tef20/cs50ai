import copy

EMPTY = None
O = "O"
X = "X"


def player(board):
    """
    Returns player who has the next turn on a board, with X to start.
    """
    plays = 0
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] != EMPTY:
                plays += 1
    if plays % 2 == 0:
        return X
    else:
        return O

board = [[X, O, X],
            [O, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

board1 = [[X, O, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

board2 = [[X, EMPTY, EMPTY],
            [EMPTY, X, EMPTY],
            [EMPTY, EMPTY, X]]

board3 = [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    for i in range(3):
        if board[i][0] and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
    for j in range(3):
        if board[0][j] and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

print(winner(board2))

