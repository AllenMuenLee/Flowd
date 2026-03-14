def place_marker(board, marker, position):
    """
    Places the player's marker on the board at the specified position.

    Parameters:
    board (list): The current state of the Tic Tac Toe board.
    marker (str): The marker to place on the board ('X' or 'O').
    position (int): The position on the board to place the marker (1-9).

    Returns:
    None
    """
    board[position - 1] = marker
