from tkinter import *
from timeit import default_timer as timer
from tkinter import messagebox, simpledialog
import threading
import copy

from sudokucsp import SudokuCSP
import SudokoGenarator
from csp import backtracking_search, mrv, unordered_domain_values, forward_checking, mac, no_inference

size = 9  # Size of the Sudoku board
MARGIN = 20  # Pixels around the board
SIDE = 50  # Width of every board cell
WIDTH_B = HEIGHT_B = MARGIN * 2 + SIDE * size  # Width and height of the whole board
WIDTH = WIDTH_B + 180  # Width of board and buttons solve and reset


class SudokuUI(Frame):

    def __init__(self, parent):
        self.parent = parent
        self.original_board = [[0 for _ in range(size)] for _ in range(size)]
        self.current_board = copy.deepcopy(self.original_board)
        Frame.__init__(self, parent)
        self.row, self.col = 0, 0
        self.__initUI()

    def __initUI(self):
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=WIDTH_B, height=HEIGHT_B)
        self.canvas.pack(fill=BOTH, side=TOP)
        self.canvas.grid(row=0, column=0, rowspan=30, columnspan=60)

        self.level = IntVar(value=1)
        self.which = 0

        self.time = StringVar()
        self.time.set("Time:                    ")
        self.n_bt = StringVar()
        self.n_bt.set("N. BT:   ")

        self.make_menu()

        self.__change_level()

        self.clear_button = Button(self, text="Reset", command=self.__clear_board, width=15, height=5)
        self.clear_button.grid(row=10, column=61, padx=20, columnspan=3)
        self.solve_button = Button(self, text="Solve", command=self.solve_clicked, width=15, height=5)
        self.solve_button.grid(row=13, column=61, padx=20, columnspan=3)

        lbltime = Label(self, textvariable=self.time)
        lblBT = Label(self, textvariable=self.n_bt)

        Label(self, text="Inference:               ").grid(row=14, column=61)
        lbltime.grid(row=30, column=0)

        lblBT.grid(row=32, column=0)
        self.inference = StringVar()
        self.radio = []
        self.radio.append(Radiobutton(self, text="No Inference", variable=self.inference, value="NO_INFERENCE"))
        self.radio[0].grid(row=15, column=62, padx=2)
        self.radio.append(Radiobutton(self, text="FC                  ", variable=self.inference, value="FC"))
        self.radio[1].grid(row=16, column=62)
        self.radio.append(Radiobutton(self, text="MAC              ", variable=self.inference, value="MAC"))
        self.radio[2].grid(row=17, column=62)
        self.inference.set("NO_INFERENCE")

        Label(self, text="Variable to choose:").grid(row=18, column=61)
        lbltime.grid(row=30, column=0)

        lblBT.grid(row=32, column=0)

        self.var_to_choose = StringVar()
        self.radio.append(Radiobutton(self, text="MRV", variable=self.var_to_choose, value="MRV"))
        self.radio[3].grid(row=20, column=62)

        self.var_to_choose.set("MRV")

        self.__draw_grid()
        self.__draw_puzzle()

        # Bind the function to validate user input
        self.canvas.bind("<Button-1>", self.on_cell_click)

    def solve_clicked(self):
        for rb in self.radio:
            rb.config(state=DISABLED)
        self.clear_button.config(state=DISABLED)
        self.solve_button.config(state=DISABLED)
        self.menu_bar.entryconfig("Level", state="disabled")
        p = threading.Thread(target=self.solve_sudoku)
        p.start()
        messagebox.showinfo("Working", "We are looking for a solution, please wait some seconds ...")

    def solve_sudoku(self):
        s = SudokuCSP(self.current_board)
        inf, dv, suv = None, None, None

        if self.inference.get() == "NO_INFERENCE":
            inf = no_inference
        elif self.inference.get() == "FC":
            inf = forward_checking
        elif self.inference.get() == "MAC":
            inf = mac

        if self.var_to_choose.get() == "MRV":
            suv = mrv

        start = timer()
        a = backtracking_search(s, select_unassigned_variable=suv, order_domain_values=unordered_domain_values,
                                inference=inf)
        end = timer()

        if a:
            for i in range(size):
                for j in range(size):
                    index = i * size + j
                    self.current_board[i][j] = a.get("CELL" + str(index))
        else:
            messagebox.showerror("Error", "Invalid sudoku puzzle, please check the initial state")

        self.__draw_puzzle()
        self.time.set("Time: " + str(round(end - start, 5)) + " seconds")
        self.n_bt.set("N. BR: " + str(s.n_bt))

        for rb in self.radio:
            rb.config(state=NORMAL)
        self.clear_button.config(state=NORMAL)
        self.solve_button.config(state=NORMAL)
        self.menu_bar.entryconfig("Level", state="normal")

    def make_menu(self):
        self.menu_bar = Menu(self.parent)
        self.parent.configure(menu=self.menu_bar)
        level_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Level", menu=level_menu)
        level_menu.add_radiobutton(label="Easy", variable=self.level, value=1, command=self.__change_level)
        level_menu.add_radiobutton(label="Hard", variable=self.level, value=2, command=self.__change_level)

    def __change_level(self):
        sudoku_board = SudokoGenarator.generate_sudoku()
        num_to_remove = 40  # Adjust the number of removed elements as needed
        SudokoGenarator.remove_numbers(sudoku_board, num_to_remove)
        self.original_board = copy.deepcopy(sudoku_board)
        self.current_board = copy.deepcopy(self.original_board)
        self.__draw_puzzle()

    def __draw_grid(self):
        for i in range(10):
            if i % 3 == 0:
                color = "black"
            else:
                color = "gray"
            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT_B - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)
            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH_B - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        self.time.set("Time:                  ")
        self.n_bt.set("N. BT:   ")
        for i in range(size):
            for j in range(size):
                cell = self.current_board[i][j]
                if cell != 0:
                    x = MARGIN + j * SIDE + SIDE / 2
                    y = MARGIN + i * SIDE + SIDE / 2
                    if str(cell) == str(self.original_board[i][j]):
                        self.canvas.create_text(x, y, text=cell, tags="numbers", fill="black")
                    else:
                        self.canvas.create_text(x, y, text=cell, tags="numbers", fill="red")

    def __clear_board(self):
        sudoku_board = SudokoGenarator.generate_sudoku()
        num_to_remove = 40  # Adjust the number of removed elements as needed
        SudokoGenarator.remove_numbers(sudoku_board, num_to_remove)
        self.original_board = copy.deepcopy(sudoku_board)
        self.current_board = copy.deepcopy(self.original_board)
        self.__draw_puzzle()

    def on_cell_click(self, event):
        x, y = event.x, event.y
        col = (x - MARGIN) // SIDE
        row = (y - MARGIN) // SIDE
        if 0 <= row < size and 0 <= col < size:
            self.row, self.col = row, col
            self.canvas.focus_set()

            # Get user input using a simple dialog
            user_input = simpledialog.askinteger("Input", "Enter a number (1-9):", parent=self.parent, minvalue=1, maxvalue=9)

            if user_input is not None:
                if self.is_valid_input(user_input, row, col):
                    self.current_board[row][col] = user_input
                    self.__draw_puzzle()
                else:
                    messagebox.showerror("Invalid Input", "Invalid input in cell ({}, {}). Please try again.".format(row, col))

    def is_valid_input(self, num, row, col):
        if num in self.current_board[row] or num in [self.current_board[i][col] for i in range(size)]:
            return False

        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if self.current_board[start_row + i][start_col + j] == num:
                    return False

        return True