def check_win(board, marker):
    """
    Check if the specified marker has won the game.

    Parameters:
    board (list): The current state of the Tic Tac Toe board.
    marker (str): The marker to check for a win ('X' or 'O').

    Returns:
    bool: True if the marker has won, False otherwise.
    """
    # Check rows for win
    for row in board:
        if all([cell == marker for cell in row]):
            return True

    # Check columns for win
    for col in range(3):
        if all([board[row][col] == marker for row in range(3)]):
            return True

    # Check diagonals for win
    if all([board[i][i] == marker for i in range(3)]) or all([board[i][2-i] == marker for i in range(3)]):
        return True

    return False
