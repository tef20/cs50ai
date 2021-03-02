import itertools
import copy
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __sub__(self, other):
        return Sentence(self.cells - other.cells, self.count - other.count)

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        - mine(s) can be inferred when the number of known mines (count)
          matches the number of cells under consideration.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        - safe(s) can be inferred when the number of known mines (count)
          reaches zero.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
         - removes known mine from list of unknowns, decrements count.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
         - removes known safe from list of unknowns.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def explore_neighbours(self, cell, count):
        neighbours = set()
        known_mines = 0
        # explore neighbouring cells (surrounding 3 x 3 grid)
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Update count if cell in bounds and unexplored
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.moves_made:
                        if (i, j) not in self.mines:
                            if (i, j) not in self.safes:
                                neighbours.add((i, j))
                        elif (i, j) in self.mines:
                            known_mines += 1
        return neighbours, count - known_mines

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # register move made
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # group unidentified neighbours and mine count
        unsolved_neighbours, unsolved_mines = self.explore_neighbours(cell, count)
        self.knowledge.append(Sentence(unsolved_neighbours, unsolved_mines))

        # generate all possible new inferences and sentences in knowledge
        to_update = 1
        while to_update:
            self.infer_from_knowledge()
            to_update = self.new_sentence_from_knowledge()

    def infer_from_knowledge(self):
        """
        Scan sentences in knowledge to see which now implicate
        safe cells or mines. Update sentences where possible.
        """
        for s in self.knowledge:
            safes_list = copy.deepcopy(s.known_safes())
            if safes_list:
                for safe in safes_list:
                    self.mark_safe(safe)

            mines_list = copy.deepcopy(s.known_mines())
            if mines_list:
                for mine in mines_list:
                    self.mark_mine(mine)

    def new_sentence_from_knowledge(self):
        """
        Compare sentences in knowledge to identify none-empty, proper
        subsets. Generate new, more specific sentences, based on
        subset rule.
        """
        updates = 0

        for s1 in self.knowledge:
            for s2 in self.knowledge:
                # check non-empty s1 set is subset of s2 set
                if s1.cells and s1.cells < s2.cells:
                    # subtract subset from superset and add to knowledge
                    difference = copy.deepcopy(s2) - s1
                    self.knowledge.append(difference)
                    # remove redundant superset
                    self.knowledge.remove(s2)
                    updates += 1
        # updated sentences must be assessed for new inferences
        return updates

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        options = list(copy.deepcopy(self.safes) - self.moves_made)
        if options:
            return options.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # seen = copy.deepcopy(self.moves_made)
        # mines = copy.deepcopy(self.mines)

        for i in itertools.product(range(self.height), range(self.width)):
            if i not in self.moves_made and i not in self.mines:
                return i