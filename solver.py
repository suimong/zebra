"""solver.py

Solve the Einstein puzzle using Raymond Hettinger's approach.
"""

from __future__ import annotations

from typing import List, Tuple, Type

import sat_utils

from clues import (
    Clue,
    comb,
    found_at,
    same_house,
    consecutive,
    beside,
    left_of,
    right_of,
    one_between,
    two_between,
)

from literals import (
    Literal,
    Color,
    Nationality,
    Animal,
    Drink,
    Cigar,
    Children,
    Mothers,
    Foods,
    Flowers,
)


class Puzzle:
    """
    A Puzzle is defined as a collection of constraints and clues.

    Clues are subclassess of Clue. They represent information about the puzzle that can be used by
    a human to solve it, like "the man who drinks tea owns a cat." Clues aren't converted to CNF
    until the `as_cnf` method is called.

    Constraints are structural properties of the puzzle, given to us in CNF to start. They're
    things like "each house gets exactly one type of flower" and "each flower must be assigned
    to one house."

    We can add constraints and clues with `add_constraint` and `add_clue`. Both of these return
    the instance, so they can be chained together for readability.

    Since in constraint satisfaction land, clues and constraints are the same thing (they're just
    logical clauses), we lump them all together at solve time.
    """

    def __init__(self, elements: List[Type[Literal]], n_houses: int = 5) -> None:
        self.element_classes = elements
        self.houses = range(1, n_houses + 1)
        self.clues: List[Clue] = []
        self.constraints: List[Tuple[str]] = []

    def add_constraint(self, constraints: List[Tuple[str]]) -> Puzzle:
        self.constraints.extend(constraints)
        return self

    def add_clue(self, clue: Clue) -> Puzzle:
        self.clues.append(clue)
        return self

    def as_cnf(self) -> List[Tuple[str]]:
        """Express puzzle as solvable CNF"""

        # this would be a comprehension if we could use iterable unpacking
        cnf = []
        for clue in self.clues:
            cnf.extend(clue.as_cnf())

        cnf.extend(self.constraints)
        return cnf

    def __repr__(self) -> str:

        s = f"This puzzle has {len(self.houses)} houses with different people in them:\n"
        for puzzle_element in self.element_classes:
            s += f" - {puzzle_element.description()} \n"

        s += "\n"
        for i, clue in enumerate(self.clues):
            s += f"{i + 1}. {clue}\n"

        return s


"""
Original version

Taken straight from rhettinger.github.io and the associated talk.

Entities:
 * There are five houses in unique colors: Blue, green, red, white and yellow.
 * In each house lives a person of unique nationality: British, Danish, German, Norwegian and Swedish.
 * Each person drinks a unique beverage: Beer, coffee, milk, tea and water.
 * Each person smokes a unique cigar brand: Blue Master, Dunhill, Pall Mall, Prince and blend.
 * Each person keeps a unique pet: Cats, birds, dogs, fish and horses.

Constraints:
 * The Brit lives in a red house.
 * The Swede keeps dogs as pets.
 * The Dane drinks tea.
 * The green house is on the left of the white, next to it.
 * The green house owner drinks coffee.
 * The person who smokes Pall Mall rears birds.
 * The owner of the yellow house smokes Dunhill.
 * The man living in the house right in the center drinks milk.
 * The Norwegian lives in the first house.
 * The man who smokes blend lives next to the one who keeps cats.
 * The man who keeps horses lives next to the man who smokes Dunhill.
 * The owner who smokes Blue Master drinks beer.
 * The German smokes Prince.
 * The Norwegian lives next to the blue house.
 * The man who smokes blend has a neighbor who drinks water.

For each house, find out what color it is, who lives there, what they drinkk, what
they smoke, and what pet they own.
"""


enum_classes: List[Type[Literal]] = [Color, Nationality, Animal, Drink, Cigar]
literals: List[Literal] = [el for group in enum_classes for el in group]

# set up the puzzle with constraints and clues
puzzle = Puzzle(elements=[Color, Nationality, Drink, Cigar, Animal])

# # each house gets exactly one value from each attribute group
for house in puzzle.houses:
    for enum_type in enum_classes:
        puzzle.add_constraint(sat_utils.one_of(comb(value, house) for value in enum_type))

# each value gets assigned to exactly one house
for literal in literals:
    puzzle.add_constraint(sat_utils.one_of(comb(literal, house) for house in puzzle.houses))

print(Color.description())
print(Nationality)

puzzle = (
    puzzle.add_clue(same_house(Nationality.brit, Color.red))
    .add_clue(same_house(Nationality.swede, Animal.dog))
    .add_clue(same_house(Nationality.dane, Drink.tea))
    .add_clue(consecutive(Color.green, Color.white))
    .add_clue(same_house(Color.green, Drink.coffee))
    .add_clue(same_house(Cigar.pall_mall, Animal.bird))
    .add_clue(same_house(Color.yellow, Cigar.dunhill))
    .add_clue(found_at(Drink.milk, 3))
    .add_clue(found_at(Nationality.norwegian, 1))
    .add_clue(beside(Cigar.blends, Animal.cat))
    .add_clue(beside(Animal.horse, Cigar.dunhill))
    .add_clue(same_house(Cigar.blue_master, Drink.root_beer))
    .add_clue(same_house(Nationality.german, Cigar.prince))
    .add_clue(beside(Nationality.norwegian, Color.blue))
    .add_clue(beside(Cigar.blends, Drink.water))
)

print(puzzle)

sols = sat_utils.solve_all(puzzle.as_cnf())
print(f"{len(sols)} solutions found")
for sol in sols:
    print(sol)

"""
Quag's version

In honor of Mother's Day, a feast is being held to celebrate five Moms: Aniya, Holly,
Janelle, Kailyn, and Penny. Each Mom will be served by their son or daughter (Bella,
Fred, Meredith, Samantha, and Timothy), who will also place a bouquet of flowers
(Carnations, Daffodils, Lilies, Roses, or Tulips) at their Mom's place setting and
prepare a meal for them (Grilled Cheese, Pizza, Spaghetti, Stew, or Stir Fry).

The seats are arranged in a straight line at the head table, with the first being
the furthest to the left (from our perspective, not the Mom's perspectives).

Also, when it says there is "one chair" between two people, it means one person might
be in the second chair while the other person is in the fourth (i.e. there is one chair
in between them that neither is sitting in).
"""


enum_classes: List[Type[Literal]] = [Mothers, Children, Flowers, Foods]
literals = [el for group in enum_classes for el in group]

# set up the puzzle with constraints and clues
puzzle = Puzzle(elements=[Mothers, Children, Flowers, Foods])

# each house gets exactly one value from each attribute group
for house in puzzle.houses:
    for group in enum_classes:
        puzzle.add_constraint(sat_utils.one_of(comb(value, house) for value in group))

# each value gets assigned to exactly one house
for literal in literals:
    puzzle.add_constraint(sat_utils.one_of(comb(literal, house) for house in puzzle.houses))


puzzle = (
    # 1. There is one chair between the place setting with Lilies and the one eating Grilled Cheese.
    puzzle.add_clue(one_between(Flowers.lilies, Foods.grilled_cheese))
    # 2. There is one chair between Timothy's Mom and the one eating Stew.
    .add_clue(one_between(Children.timothy, Foods.stew))
    # 3. There are two chairs between the Bella's Mom and Penny's seat on the right.
    .add_clue(two_between(Children.bella, Mothers.penny))
    .add_clue(right_of(Mothers.penny, Children.bella))
    # 4. There is one chair between the place setting with Roses and the one eating Spaghetti on the left.
    .add_clue(one_between(Flowers.roses, Foods.spaghetti))
    .add_clue(left_of(Foods.spaghetti, Flowers.roses))
    # 5. There are two chairs between the place setting with Carnations and Samantha's Mom.
    .add_clue(two_between(Flowers.carnations, Children.samantha))
    # 6. There is one chair between Meredith's Mom and Timothy's Mom on the left.
    .add_clue(one_between(Children.meredith, Children.timothy))
    .add_clue(left_of(Children.timothy, Children.meredith))
    # 7. Aniya's place setting has a lovely Carnation bouquet.
    .add_clue(same_house(Mothers.aniya, Flowers.carnations))
    # 8. There are two chairs between the one eating Grilled Cheese and the one eating Spaghetti.
    .add_clue(two_between(Foods.grilled_cheese, Foods.spaghetti))
    # 9. The person in the first chair (left-most) is eating Pizza.
    .add_clue(found_at(Foods.pizza, 1))
    # 10. The Tulips were placed at one of the place settings somewhere to the left of Penny's chair.
    .add_clue(left_of(Flowers.tulips, Mothers.penny))
    # 11. There are two chairs between the one eating Spaghetti and Kailyn's seat.
    .add_clue(two_between(Foods.spaghetti, Mothers.kailyn))
    # 12. There is one chair between the one eating Pizza and Holly's chair on the right.
    .add_clue(one_between(Foods.pizza, Mothers.holly))
    .add_clue(right_of(Mothers.holly, Foods.pizza))
)

print(puzzle)
all_solutions = sat_utils.solve_all(puzzle.as_cnf())
print(f"{len(all_solutions)} solutions found")
print(all_solutions)
