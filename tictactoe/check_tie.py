def check_tie(board):
    """
    Check if the game is a tie.

    Parameters:
    board (list): The current state of the Tic Tac Toe board.

    Returns:
    bool: True if the game is a tie, False otherwise.
    """
    for row in board:
        if'' in row:
            return False
    return True
