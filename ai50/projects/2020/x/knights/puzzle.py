from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # Base knowledge:
    #  - A must be either a knight or a knave...
    Or(AKnight, AKnave),
    #  - ...but not both
    Not(And(AKnight, AKnave)),

    # New knowledge:
    #  - if A is knight, then A's statement is True
    Implication(AKnight, And(AKnight, AKnave)),
    #  - if A is knave, then A's statement is False
    Implication(AKnave, Not(And(AKnight, AKnave)))
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # Base knowledge:
    #  - A, B, C must each be either a knight or a knave...
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    #  - ...but not both
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),

    # New knowledge:
    #  - if A is knight, A's statement is True
    Implication(AKnight, And(AKnave, BKnave)),
    #  - if A is knave, A's statement is False
    Implication(AKnave, Not(And(AKnave, BKnave)))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # Base knowledge:
    #  - A, B, C must each be either a knight or a knave...
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    #  - ...but not both
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),

    # New knowledge:
    #  - if A is knight, then A statement True
    Implication(AKnight, BKnight),
    #  - if A is knave, then A statement False
    Implication(AKnave, Not(BKnave)),
    #  - if B is a knight, then B statement True
    Implication(BKnight, AKnave),
    #  - if B is knave, then B statement False
    Implication(BKnave, Not(BKnight))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # Base knowledge:
    #  - A, B, C must each be either a knight or a knave...
    Or(AKnight, AKnave),
    Or(BKnight, BKnave),
    Or(CKnight, CKnave),
    #  - ...but not both
    Not(And(AKnight, AKnave)),
    Not(And(BKnight, BKnave)),
    Not(And(CKnight, CKnave)),

    # New knowledge:
    #  - A made a statement
    Or(AKnight, AKnave),
    #  - if A is knight, B's statement is False
    Implication(AKnight, BKnave),
    #  - if A is a knave, B's statement is False
    Implication(AKnave, BKnave),
    #  - B says "C is a knave."
    Implication(BKnight, CKnave),
    Implication(BKnave, Not(CKnave)),
    #  - C says "A is a knight."
    Implication(CKnight, AKnight),
    Implication(CKnave, Not(AKnight))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
