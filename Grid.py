import random
import re
from Cell import Cell
from utils import split_word_via_api


class Grid:
    """
    The Grid class represents a grid of customizable size that contains cells in each space.

    Attributes:
        quote (str): The quote that will be placed in the grid.
        size (int): The size of the grid. Customizable via preferences.
    """
    def __init__(self, quote: str, size: int = 15, language: str = 'English', fillers: list = None):
        self.quote = quote
        self.size = size
        self.language = language
        self.fillers = fillers
        
        self.parsed_quote = self.parse_quote()

        # Try generating the grid until successful
        # (This prevents missing solutions when max_iterations is hit)
        for attempt in range(50):
            # Create grid with empty cells
            self.grid = [[Cell(row, col) for col in range(self.size)] for row in range(self.size)]
            self.starting_cell = self.starting_spot()
            
            # Start with strict adjacency rules. After 25 attempts, relax them if failing.
            strict = (attempt < 25)
            success = self.insert(self.starting_cell, strict=strict)
            if success:
                break
                
        self.fill()
        # self.print_grid()

    def get_quote(self) -> str:
        return self.quote

    def parse_quote(self) -> list:
        """
        Remove extra spaces and split via API
        """
        cleaned_quote = self.quote.strip()
        # For Telugu, we might not want to remove everything, 
        # the API should handle the string once we pass it.
        # But we should at least pass it as is or with minimal cleaning.
        return split_word_via_api(cleaned_quote, self.language)

    def print_grid(self) -> None:
        """
        Unpack each row and separate each element inside the row with a blank space. Print the result.
        ex:
            [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]
            ]

            becomes:
                1 2 3
                4 5 6
                7 8 9

        :return: None
        """
        for row in self.grid:
            print(*row, sep=' ')

    def starting_spot(self) -> Cell:
        """
        Pick a random cell to be the starting position
        :return: An empty cell
        """
        rand_row = random.randrange(self.size)
        rand_col = random.randrange(self.size)

        starting_cell = self.grid[rand_row][rand_col]

        return starting_cell

    def insert(self, start_cell: Cell, strict: bool = True) -> bool:
        """
        Insert the parsed quote into the grid using backtracking.
        :param start_cell: The starting cell
        :param strict: If True, path cannot touch itself except for the previous cell.
        :return: True if successfully inserted
        """

        self.backtrack_iterations = 0
        self.max_iterations = 50000

        def backtrack(index: int, current_cell: Cell, visited: set) -> bool:
            """
            Recursive helper function to place letters
            :param index: Index of the character in parsed_quote
            :param current_cell: The current cell to place the letter
            :param visited: Set of cell positions already used in this path

            :return: True if the quote was fully placed, False otherwise
            """
            self.backtrack_iterations += 1
            if self.backtrack_iterations > self.max_iterations:
                return False

            if index >= len(self.parsed_quote):
                return True  # All letters placed

            r, c = current_cell.get_position()
            current_cell.update_letter(self.parsed_quote[index])
            current_cell.is_snake = True
            visited.add((r, c))

            # up left, up, up right, left, right, down left, down, down right
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

            # Collect all valid neighbors
            neighbors = []
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    candidate = self.grid[nr][nc]
                    if candidate.get_empty() and (nr, nc) not in visited:
                        valid = True # Initialize valid for this candidate
                        if strict:
                            # Check to make sure only previous cell is non-empty
                            for ndr, ndc in directions:
                                nnr, nnc = nr + ndr, nc + ndc
                                if 0 <= nnr < self.size and 0 <= nnc < self.size:
                                    neighbor_cell = self.grid[nnr][nnc]
                                    if (nnr, nnc) != (r, c) and not neighbor_cell.get_empty():
                                        valid = False
                                        break
                        
                        if valid:
                            neighbors.append(candidate)

            random.shuffle(neighbors)

            # Try each neighbor recursively
            for neighbor in neighbors:
                if backtrack(index + 1, neighbor, visited):
                    return True

            # Backtrack: undo current cell
            current_cell.empty = True
            current_cell.letter = 'None'
            current_cell.is_snake = False
            visited.remove((r, c))
            return False

        # Start backtracking from the initial cell
        # We need to explicitly place the first letter in the starting cell
        start_r, start_c = start_cell.get_position()
        
        # Start the recursive search
        return backtrack(0, start_cell, set())

    def fill(self) -> None:
        """
        Loops through the grid and assigns a filler letter to every empty cell.
        """
        filler_idx = 0
        for row in self.grid:
            for cell in row:
                if cell.empty:
                    if self.fillers and filler_idx < len(self.fillers):
                        cell.update_letter(self.fillers[filler_idx])
                        filler_idx += 1
                    else:
                        cell.random_letter()
