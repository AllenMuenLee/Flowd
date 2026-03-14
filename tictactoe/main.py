from display_board import display_board
from player_input import get_player_move
from place_marker import place_marker
from check_win import check_win
from check_tie import check_tie
from replay import ask_replay

def main():
    """
    Main function to run the Tic Tac Toe game.
    """
    while True:
        board = [' '] * 9
        current_marker = 'X'
        
        while True:
            display_board(board)
            position = get_player_move(board)
            place_marker(board, current_marker, position + 1)
            
            if check_win(board, current_marker):
                display_board(board)
                print(f"Player {current_marker} wins!")
                break
            elif check_tie(board):
                display_board(board)
                print("The game is a tie!")
                break
            
            current_marker = 'O' if current_marker == 'X' else 'X'
        
        if ask_replay()!= 'y':
            break

if __name__ == "__main__":
    main()