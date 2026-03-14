def get_player_move(board):
    """
    Prompts the player for their next move and returns the position on the board.
    
    Parameters:
    board (list): The current state of the Tic Tac Toe board.
    
    Returns:
    int: The position on the board where the player wants to place their marker.
    """
    while True:
        try:
            move = int(input("Enter your next move (1-9): "))
            if 1 <= move <= 9 and board[move - 1] == ' ':
                return move - 1
            else:
                print("Invalid move. Please choose an empty position (1-9).")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 9.")
