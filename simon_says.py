import random
import time

COLORS = ["red", "blue", "green", "yellow"]
NUMBER_TO_COLOR = {str(index): color for index, color in enumerate(COLORS, start=1)}


def show_sequence(sequence):
    """Show the sequence, then clear it from the terminal."""
    print("\nWatch the sequence:")
    for color in sequence:
        print(color.upper())
        time.sleep(0.6)
    print("\n" * 30)


def get_player_sequence(length):
    """Read and validate the player's sequence."""
    print("Repeat the sequence using color names or 1=red, 2=blue, 3=green, 4=yellow.")
    answers = []

    while len(answers) < length:
        entry = input(f"Color {len(answers) + 1}: ").strip().lower()
        color = NUMBER_TO_COLOR.get(entry, entry)
        if color not in COLORS:
            print("Enter red, blue, green, yellow, or a number from 1 to 4.")
            continue
        answers.append(color)

    return answers


def play_game():
    """Play until the sequence is entered incorrectly."""
    sequence = []
    score = 0

    print("\n=== Simon Says ===")
    print("Memorize each sequence and repeat it in the same order.")

    while True:
        sequence.append(random.choice(COLORS))
        show_sequence(sequence)

        if get_player_sequence(len(sequence)) != sequence:
            print(f"\nGame over! Your score: {score}")
            return

        score += 1
        print(f"Correct! Score: {score}")
        time.sleep(0.7)


def main():
    while True:
        print("\n1. Play")
        print("2. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            play_game()
        elif choice == "2":
            print("Thanks for playing!")
            break
        else:
            print("Please choose 1 or 2.")


if __name__ == "__main__":
    main()
