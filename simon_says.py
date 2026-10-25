"""Repeat the growing color sequence for as long as you can."""

import random
import time


COLORS = ("red", "blue", "green", "yellow")


def get_player_sequence():
    """Read a sequence of color names, or None if the player quits."""
    response = input("Repeat the colors, separated by spaces (or q to quit): ")
    if response.strip().lower() == "q":
        return None
    return response.strip().lower().split()


def play_game():
    """Play one game and return the highest completed round."""
    sequence = []
    score = 0

    print("\n=== Simon Says ===")
    print("Watch the sequence, then repeat it using color names.")
    print("Available colors: red, blue, green, yellow")

    while True:
        sequence.append(random.choice(COLORS))
        print(f"\nRound {len(sequence)}")
        print(" ".join(sequence))
        time.sleep(1)

        player_sequence = get_player_sequence()
        if player_sequence is None:
            print("You ended the game.")
            break
        if player_sequence != sequence:
            print("Wrong sequence!")
            break

        score += 1
        print("Correct!")

    print(f"Game over! You completed {score} round(s).")
    return score


def main():
    """Run the game menu."""
    print("=== Simon Says ===")

    while True:
        print("\n1. Play")
        print("2. Exit")
        choice = input("Choose an option (1/2): ").strip()

        if choice == "1":
            play_game()
        elif choice == "2":
            print("Goodbye!")
            return
        else:
            print("Invalid choice! Please choose 1 or 2.")


if __name__ == "__main__":
    main()
