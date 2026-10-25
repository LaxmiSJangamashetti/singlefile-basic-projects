from __future__ import annotations

import random
import time
import tkinter as tk
from tkinter import messagebox, ttk


class Sudoku:
    """Sudoku board generation and solving helpers."""

    @staticmethod
    def candidates(board: list[list[int]], row: int, col: int) -> list[int]:
        used = set(board[row])
        used.update(board[r][col] for r in range(9))
        box_row, box_col = row // 3 * 3, col // 3 * 3
        used.update(board[r][c] for r in range(box_row, box_row + 3)
                    for c in range(box_col, box_col + 3))
        return [n for n in range(1, 10) if n not in used]

    @classmethod
    def fill(cls, board: list[list[int]]) -> bool:
        best: tuple[int, int, list[int]] | None = None
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    options = cls.candidates(board, r, c)
                    if not options:
                        return False
                    if best is None or len(options) < len(best[2]):
                        best = (r, c, options)
        if best is None:
            return True
        r, c, options = best
        random.shuffle(options)
        for value in options:
            board[r][c] = value
            if cls.fill(board):
                return True
        board[r][c] = 0
        return False

    @classmethod
    def solution(cls) -> list[list[int]]:
        board = [[0] * 9 for _ in range(9)]
        cls.fill(board)
        return board

    @classmethod
    def count_solutions(cls, board: list[list[int]], limit: int = 2) -> int:
        """Count solutions up to limit, stopping early for ambiguous boards."""
        best: tuple[int, int, list[int]] | None = None
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    options = cls.candidates(board, r, c)
                    if not options:
                        return 0
                    if best is None or len(options) < len(best[2]):
                        best = (r, c, options)
        if best is None:
            return 1
        r, c, options = best
        total = 0
        for value in options:
            board[r][c] = value
            total += cls.count_solutions(board, limit - total)
            board[r][c] = 0
            if total >= limit:
                return total
        return total


class SudokuApp:
    BG = "#f4f7fb"
    INK = "#17233c"
    MUTED = "#77839a"
    BLUE = "#3867e8"
    PALE_BLUE = "#e8efff"
    GREEN = "#17885a"
    RED = "#d74d5b"
    GRID = "#cbd3e0"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Sudoku · Daily Focus")
        root.configure(bg=self.BG)
        root.resizable(False, False)

        self.difficulty = tk.StringVar(value="Easy")
        self.status = tk.StringVar(value="Choose a square and enter a number")
        self.timer_text = tk.StringVar(value="00:00")
        self.selected: tuple[int, int] | None = None
        self.solution: list[list[int]] = []
        self.puzzle: list[list[int]] = []
        self.values: list[list[int]] = []
        self.given: list[list[bool]] = []
        self.entries: list[list[tk.Label]] = []
        self.started_at = time.monotonic()
        self.finished = False

        self.build_ui()
        self.new_game()
        self.root.bind("<Key>", self.on_key)
        self.root.bind("<BackSpace>", lambda _event: self.erase_cell())
        self.root.bind("<Delete>", lambda _event: self.erase_cell())
        self.root.bind("<Escape>", lambda _event: self.clear_selection())
        self.root.bind("<Left>", lambda _event: self.move_selection(0, -1))
        self.root.bind("<Right>", lambda _event: self.move_selection(0, 1))
        self.root.bind("<Up>", lambda _event: self.move_selection(-1, 0))
        self.root.bind("<Down>", lambda _event: self.move_selection(1, 0))
        self.update_timer()

    def build_ui(self) -> None:
        page = tk.Frame(self.root, bg=self.BG, padx=30, pady=22)
        page.pack()

        header = tk.Frame(page, bg=self.BG)
        header.pack(fill="x", pady=(0, 17))
        tk.Label(header, text="▦", font=("Segoe UI Symbol", 24), fg=self.BLUE,
                 bg=self.BG).pack(side="left", padx=(0, 11))
        titles = tk.Frame(header, bg=self.BG)
        titles.pack(side="left")
        tk.Label(titles, text="SUDOKU", font=("Segoe UI", 20, "bold"),
                 fg=self.INK, bg=self.BG).pack(anchor="w")
        tk.Label(titles, text="A little focus goes a long way.",
                 font=("Segoe UI", 10), fg=self.MUTED, bg=self.BG).pack(anchor="w")
        timer_box = tk.Frame(header, bg="white", padx=13, pady=8,
                             highlightthickness=1, highlightbackground="#e2e7ef")
        timer_box.pack(side="right", padx=(15, 0))
        tk.Label(timer_box, text="TIME", font=("Segoe UI", 8, "bold"),
                 fg=self.MUTED, bg="white").pack()
        tk.Label(timer_box, textvariable=self.timer_text, font=("Consolas", 16, "bold"),
                 fg=self.INK, bg="white").pack()

        bar = tk.Frame(page, bg=self.BG)
        bar.pack(fill="x", pady=(0, 12))
        tk.Label(bar, text="DIFFICULTY", font=("Segoe UI", 9, "bold"),
                 fg=self.MUTED, bg=self.BG).pack(side="left", padx=(0, 8))
        style = ttk.Style()
        style.configure("Sudoku.TCombobox", padding=5)
        self.difficulty_box = ttk.Combobox(bar, textvariable=self.difficulty,
                                           values=("Easy", "Medium", "Hard"),
                                           state="readonly", width=10,
                                           style="Sudoku.TCombobox")
        self.difficulty_box.pack(side="left")
        self.button(bar, "＋  New game", self.new_game, self.BLUE, "white").pack(side="right")

        board_frame = tk.Frame(page, bg=self.INK, padx=2, pady=2)
        board_frame.pack()
        for r in range(9):
            row: list[tk.Label] = []
            for c in range(9):
                cell = tk.Label(board_frame, text="", width=3, height=1,
                                font=("Segoe UI", 19), bg="white", fg=self.INK,
                                cursor="hand2", anchor="center", padx=0, pady=5,
                                highlightthickness=0)
                cell.grid(row=r, column=c,
                          padx=(0 if c % 3 == 0 else 1, 2 if c % 3 == 2 else 1),
                          pady=(0 if r % 3 == 0 else 1, 2 if r % 3 == 2 else 1))
                cell.bind("<Button-1>", lambda _e, rr=r, cc=c: self.select_cell(rr, cc))
                row.append(cell)
            self.entries.append(row)

        keypad = tk.Frame(page, bg=self.BG)
        keypad.pack(pady=(14, 8))
        for value in range(1, 10):
            self.button(keypad, str(value), lambda n=value: self.enter_number(n),
                        "white", self.INK, border=True).grid(row=0, column=value - 1,
                                                             padx=3, ipadx=3)

        actions = tk.Frame(page, bg=self.BG)
        actions.pack(fill="x", pady=(4, 8))
        self.button(actions, "⌫  Erase", self.erase_cell, "white", self.INK,
                    border=True).pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.button(actions, "✦  Hint", self.give_hint, self.PALE_BLUE,
                    self.BLUE).pack(side="left", expand=True, fill="x", padx=5)
        self.button(actions, "✓  Check", self.check_board, "#e8f6ef",
                    self.GREEN).pack(side="left", expand=True, fill="x", padx=5)
        self.button(actions, "Show solution", self.show_solution, "white",
                    self.MUTED, border=True).pack(side="left", expand=True,
                                                  fill="x", padx=(5, 0))
        tk.Label(page, textvariable=self.status, font=("Segoe UI", 10),
                 fg=self.MUTED, bg=self.BG).pack(pady=(7, 0))

    @staticmethod
    def button(parent: tk.Widget, text: str, command, bg: str, fg: str,
               border: bool = False) -> tk.Button:
        return tk.Button(parent, text=text, command=command,
                         font=("Segoe UI", 10, "bold"), bg=bg, fg=fg,
                         activebackground=bg, activeforeground=fg,
                         relief="solid" if border else "flat",
                         bd=1 if border else 0, highlightthickness=0,
                         padx=10, pady=7, cursor="hand2")

    def new_game(self) -> None:
        level = self.difficulty.get()
        clues = {"Easy": 40, "Medium": 32, "Hard": 27}[level]
        self.status.set("Creating a new puzzle…")
        self.root.update_idletasks()
        self.solution = Sudoku.solution()
        self.puzzle = [row[:] for row in self.solution]
        cells = list(range(81))
        random.shuffle(cells)
        removed = 0
        target = 81 - clues
        for pos in cells:
            if removed >= target:
                break
            r, c = divmod(pos, 9)
            previous = self.puzzle[r][c]
            self.puzzle[r][c] = 0
            if Sudoku.count_solutions(self.puzzle) == 1:
                removed += 1
            else:
                self.puzzle[r][c] = previous
        self.values = [row[:] for row in self.puzzle]
        self.given = [[value != 0 for value in row] for row in self.puzzle]
        self.selected = None
        self.finished = False
        self.started_at = time.monotonic()
        self.status.set("Choose a square and enter a number")
        self.render()

    def render(self) -> None:
        for r in range(9):
            for c in range(9):
                cell = self.entries[r][c]
                value = self.values[r][c]
                bg, fg, font = "white", self.INK, ("Segoe UI", 19)
                if self.given[r][c]:
                    fg, font = "#26344f", ("Segoe UI", 19, "bold")
                if value and not self.given[r][c]:
                    fg = self.BLUE
                if self.selected == (r, c):
                    bg = "#dce7ff"
                elif self.selected and (r == self.selected[0] or c == self.selected[1]):
                    bg = "#f0f4ff"
                elif self.selected and value and value == self.values[self.selected[0]][self.selected[1]]:
                    bg = "#e7edfa"
                if value and not self.given[r][c] and value != self.solution[r][c]:
                    fg = self.RED
                cell.configure(text=str(value) if value else "", bg=bg, fg=fg, font=font)

    def select_cell(self, row: int, col: int) -> None:
        if self.finished:
            return
        self.selected = (row, col)
        self.render()

    def enter_number(self, value: int) -> None:
        if self.finished or self.selected is None:
            self.status.set("Select an empty square first")
            return
        r, c = self.selected
        if self.given[r][c]:
            self.status.set("That number is part of the puzzle")
            return
        self.values[r][c] = value
        self.render()
        self.status.set("Good start — keep going!") if value == self.solution[r][c] else self.status.set("That doesn't look right — try again")
        if self.values == self.solution:
            self.finish_game()

    def on_key(self, event: tk.Event) -> None:
        if event.char in "123456789":
            self.enter_number(int(event.char))
        elif event.char in "0 ":
            self.erase_cell()

    def erase_cell(self) -> None:
        if self.finished or self.selected is None:
            return
        r, c = self.selected
        if self.given[r][c]:
            return
        self.values[r][c] = 0
        self.render()
        self.status.set("Square cleared")

    def give_hint(self) -> None:
        if self.finished:
            return
        if self.selected is None:
            self.status.set("Select a square to get a hint")
            return
        r, c = self.selected
        if self.given[r][c]:
            self.status.set("Choose an empty square for a hint")
            return
        self.values[r][c] = self.solution[r][c]
        self.render()
        self.status.set("A little help, right where you need it")
        if self.values == self.solution:
            self.finish_game()

    def check_board(self) -> None:
        if self.finished:
            return
        wrong = sum(1 for r in range(9) for c in range(9)
                    if self.values[r][c] and self.values[r][c] != self.solution[r][c])
        empty = sum(value == 0 for row in self.values for value in row)
        if wrong:
            self.status.set(f"There {'is' if wrong == 1 else 'are'} {wrong} incorrect number{'s' if wrong != 1 else ''} in red")
        elif empty:
            self.status.set(f"So far, so good! {empty} square{'s' if empty != 1 else ''} left")
        else:
            self.finish_game()

    def show_solution(self) -> None:
        if self.finished:
            return
        if messagebox.askyesno("Show solution", "Reveal the completed puzzle? This ends your game."):
            self.values = [row[:] for row in self.solution]
            self.render()
            self.finished = True
            self.status.set("Solution revealed — start a new game when you're ready")

    def finish_game(self) -> None:
        self.finished = True
        elapsed = int(time.monotonic() - self.started_at)
        self.status.set(f"Puzzle complete! You finished in {elapsed // 60:02d}:{elapsed % 60:02d} 🎉")
        self.render()

    def move_selection(self, dr: int, dc: int) -> None:
        if self.selected is None:
            self.select_cell(0, 0)
            return
        r, c = self.selected
        self.select_cell((r + dr) % 9, (c + dc) % 9)

    def clear_selection(self) -> None:
        self.selected = None
        self.render()

    def update_timer(self) -> None:
        elapsed = int(time.monotonic() - self.started_at)
        self.timer_text.set(f"{elapsed // 60:02d}:{elapsed % 60:02d}")
        self.root.after(1000, self.update_timer)


def main() -> None:
    root = tk.Tk()
    SudokuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
