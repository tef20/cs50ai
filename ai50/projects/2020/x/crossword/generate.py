import sys
import itertools

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for x in self.crossword.words:
                if len(x) != var.length:
                    self.domains[var].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False

        if self.crossword.overlaps[x, y]:
            i, j = self.crossword.overlaps[x, y]

            for val1 in self.domains[x].copy():
                for val2 in self.domains[y]:
                    # check: different word but matching i/j-th char
                    if val1 != val2 and val1[i] == val2[j]:
                        break
                else:
                    # if no val1 - val2 overlaps found in y:
                    self.domains[x].remove(val1)
                    revision_made = True

        return revision_made

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            # initial list of all arcs in the problem
            arcs = [
                arc_pairs for arc_pairs in itertools.product(self.crossword.variables, repeat=2)
                if arc_pairs[0] != arc_pairs[1]
                ]

        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):
                if not x or not y:
                    return False  # (no way to solve problem)

                # add potentially effected neighbouring nodes
                neighbours = self.crossword.neighbors(x) - {y}
                for linked_arc in neighbours:
                    arcs.append((linked_arc, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) != len(self.crossword.variables):
            return False

        for variable in assignment:
            if not assignment[variable]:
                return False
        else:
            return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
         - all values are distinct /
         - every value is the correct length /
         - there are no conflicts between neighboring variables. /
        """
        distinct_values = set()

        for selected_variable in assignment:
            # check selected variable not empty
            if not assignment[selected_variable]:
                continue

            # check value length meets selected variable's unary constraint
            if len(assignment[selected_variable]) != selected_variable.length:
                return False

            # check for duplicated values
            if assignment[selected_variable] in distinct_values:
                return False
            else:
                distinct_values.add(assignment[selected_variable])

            # check for conflicts with neighbouring selected variables (binary constraint)
            assigned_neighbours = [n for n in self.crossword.neighbors(selected_variable) if n in assignment]
            for neighbour in assigned_neighbours:
                # get overlap points: ith letter of selected variable, jth letter of neighbour
                i, j = self.crossword.overlaps[selected_variable, neighbour]
                # check for clash
                if assignment[selected_variable][i] != assignment[neighbour][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # get var neighbours, disclude already assigned values
        neighbours = [n for n in self.crossword.neighbors(var) if n not in assignment]
        values = []

        # list values and the number of conflicts associated with them
        for val1 in self.domains[var]:
            # initialise at zero
            conflicts = 0

            for neighbour in neighbours:
                i, j = self.crossword.overlaps[var, neighbour]

                for val2 in self.domains[neighbour]:
                    # check for clash
                    if val1[i] != val2[j]:
                        conflicts += 1

            values.append((conflicts, val1))

        # order values by conflict count
        values.sort()
        # isolate values only
        values = [v[1] for v in values]

        return values

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        choice = None

        for v in self.crossword.variables:
            # select unassigneds only
            if v in assignment:
                continue

            # make initial choice
            if not choice:
                choice = v

            # chose var with minimum vals
            elif len(self.domains[v]) < len(self.domains[choice]):
                choice = v

            elif len(self.domains[v]) == len(self.domains[choice]):
                # choose var with highest degree
                if len(self.crossword.neighbors(v)) > len(self.crossword.neighbors(choice)):
                    choice = v

        return choice

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        unassigned_var = self.select_unassigned_variable(assignment)

        # self.order_domain_values(unassigned_var, assignment)
        for val in self.domains[unassigned_var]:
            assignment[unassigned_var] = val

            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result

            assignment.pop(unassigned_var)
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
