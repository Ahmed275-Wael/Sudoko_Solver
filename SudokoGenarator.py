import random


def generate_sudoku():
    size = 9
    board = [[0] * size for _ in range(size)]

    # Generate a random initial configuration for the first row
    first_row = random.sample(range(1, size + 1), size)
    for i in range(size):
        board[0][i] = first_row[i]

    def is_valid(board, row, col, num):
        # Check if the number is not present in the current row and column
        if num in board[row] or num in [board[i][col] for i in range(size)]:
            return False

        # Check if the number is not present in the 3x3 subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False

        return True

    def solve():
        for row in range(size):
            for col in range(size):
                if board[row][col] == 0:
                    for num in range(1, size + 1):
                        if is_valid(board, row, col, num):
                            board[row][col] = num

                            if solve():
                                return True  # Continue solving recursively

                            # If placing the number doesn't lead to a solution, backtrack
                            board[row][col] = 0

                    # If no number can be placed, backtrack
                    return False

        return True  # Board is solved

    # Start solving from the second row
    solve()

    return board


def remove_numbers(board, num_to_remove):
    # Create a list of all positions on the board
    positions = [(i, j) for i in range(9) for j in range(9)]

    # Shuffle the list to randomize the removal order
    random.shuffle(positions)

    # Remove numbers from the board while ensuring it remains solvable
    for pos in positions:
        row, col = pos
        original_value = board[row][col]
        board[row][col] = 0  # Remove the number

        # Check if the board is still solvable
        temp_board = [row[:] for row in board]  # Create a copy of the board
        if not solve_sudoku(temp_board):
            # If removing the number makes the board unsolvable, restore the original value
            board[row][col] = original_value

        # Check if we have removed enough numbers
        if sum(row.count(0) for row in board) >= num_to_remove:
            break


def solve_sudoku(board):
    # A simple backtracking solver for Sudoku
    def is_valid(row, col, num):
        # Check if the number is not present in the current row and column
        if num in board[row] or num in [board[i][col] for i in range(9)]:
            return False

        # Check if the number is not present in the 3x3 subgrid
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False

        return True

    def solve():
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(row, col, num):
                            board[row][col] = num

                            if solve():
                                return True  # Continue solving recursively

                            # If placing the number doesn't lead to a solution, backtrack
                            board[row][col] = 0

                    # If no number can be placed, backtrack
                    return False

        return True  # Board is solved

    return solve()


def print_sudoku(board):
    for row in board:
        print(' '.join(map(str, row)))


# Example usage:
sudoku_board = generate_sudoku()
print("Generated Sudoku:")
print_sudoku(sudoku_board)

# Remove some numbers to create a puzzle
num_to_remove = 40  # Adjust the number of removed elements as needed
remove_numbers(sudoku_board, num_to_remove)

print("\nSudoku Puzzle:")
print_sudoku(sudoku_board)
