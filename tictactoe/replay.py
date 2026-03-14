def ask_replay():
    """
    Asks the players if they want to play again.

    Returns:
        str: 'y' if players want to play again, 'n' otherwise.
    """
    while True:
        replay = input("Do you want to play again? Enter Yes or No: ").lower()
        if replay in ['yes', 'y']:
            return 'y'
        elif replay in ['no', 'n']:
            return 'n'
        else:
            print("Please enter Yes or No.")
