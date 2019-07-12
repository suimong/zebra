"""solver.py

Solve the Einstein puzzle using Raymond Hettinger's approach.
"""


from itertools import product
from typing import List, Tuple, Union

import sat_utils
from sat_utils import CNF, Element


def comb(value: str, house: int) -> Element:
    """Format how a value is shown at a given house"""

    return f"{value} {house}"


def found_at(value: str, house: int) -> List[Tuple[Element]]:
    """Value known to be at a specific house"""

    return [(comb(value, house),)]


def same_house(value1: Element, value2: Element):
    """The two values occur in the same house: brit1 & red1 | brit2 & red2 ..."""

    return sat_utils.from_dnf((comb(value1, i), comb(value2, i)) for i in houses)


def consecutive(value1: Element, value2: Element):
    """The values are in consecutive houses: green1 & white2 | green2 & white3 ..."""

    return sat_utils.from_dnf(
        (comb(value1, i), comb(value2, j)) for i, j in zip(houses, houses[1:])
    )


def beside(value1: Element, value2: Element):
    """The values occur side-by-side: blends1 & cat2 | blends2 & cat1 ..."""

    return sat_utils.from_dnf(
        [(comb(value1, i), comb(value2, j)) for i, j in zip(houses, houses[1:])]
        + [(comb(value2, i), comb(value1, j)) for i, j in zip(houses, houses[1:])]
    )


def left_of(value1: Element, value2: Element):
    """The first value is somewhere to the left of the second value."""

    return sat_utils.from_dnf(
        (comb(value1, i), comb(value2, j)) for i, j in product(houses, houses) if i < j
    )


def right_of(value1: Element, value2: Element):
    """The first value is somewhere to the right of the second value."""

    return sat_utils.from_dnf(
        (comb(value1, i), comb(value2, j)) for i, j in product(houses, houses) if i > j
    )


def one_between(value1: Element, value2: Element):
    """The values have one other value in between: cat1 & x2 & dog3 | dog2 & x3 & cat1 ..."""

    return sat_utils.from_dnf(
        [(comb(value1, i), comb(value2, j)) for i, j in zip(houses, houses[2:])]
        + [(comb(value2, i), comb(value1, j)) for i, j in zip(houses, houses[2:])]
    )


def two_between(value1: Element, value2: Element):
    """The values have two other values in between: cat1 & x2 & y3 & dog4 | ..."""

    return sat_utils.from_dnf(
        [(comb(value1, i), comb(value2, j)) for i, j in zip(houses, houses[3:])]
        + [(comb(value2, i), comb(value1, j)) for i, j in zip(houses, houses[3:])]
    )


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

# houses = [1, 2, 3, 4, 5]

# groups = [
#     ["yellow", "red", "white", "green", "blue"],
#     ["dane", "brit", "swede", "norwegian", "german"],
#     ["horse", "cat", "bird", "fish", "dog"],
#     ["water", "tea", "milk", "coffee", "root beer"],
#     ["pall mall", "prince", "blue master", "dunhill", "blends"],
# ]

# values: List[Element] = [el for group in groups for el in group]

# # set up the puzzle with constraints and clues
# cnf: CNF = []

# # each house gets exactly one value from each attribute group
# for house in houses:
#     for group in groups:
#         cnf += sat_utils.one_of(comb(value, house) for value in group)

# # each value gets assigned to exactly one house
# for value in values:
#     cnf += sat_utils.one_of(comb(value, house) for house in houses)

# cnf += same_house("brit", "red")
# cnf += same_house("swede", "dog")
# cnf += same_house("dane", "tea")
# cnf += consecutive("green", "white")
# cnf += same_house("green", "coffee")
# cnf += same_house("pall mall", "bird")
# cnf += same_house("yellow", "dunhill")
# cnf += found_at("milk", 3)
# cnf += found_at("norwegian", 1)
# cnf += beside("blends", "cat")
# cnf += beside("horse", "dunhill")
# cnf += same_house("blue master", "root beer")
# cnf += same_house("german", "prince")
# cnf += beside("norwegian", "blue")
# cnf += beside("blends", "water")

# sat_utils.solve_one(cnf)


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

houses = [1, 2, 3, 4, 5]

groups: List[List[Element]] = [
    ["aniya", "holly", "janelle", "kailyn", "penny"],
    ["bella", "fred", "meredith", "samantha", "timothy"],
    ["carnations", "daffodils", "lilies", "roses", "tulips"],
    ["grilled cheese", "pizza", "spaghetti", "stew", "stir fry"],
]

literals: List[Element] = [el for group in groups for el in group]

# set up the puzzle with constraints and clues
cnf: CNF = []

# each house gets exactly one value from each attribute group
for house in houses:
    for group in groups:
        cnf += sat_utils.one_of(comb(value, house) for value in group)

# each value gets assigned to exactly one house
for value in literals:
    cnf += sat_utils.one_of(comb(value, house) for house in houses)


# 1. There is one chair between the place setting with Lilies and the one eating Grilled Cheese.
cnf += one_between("lilies", "grilled cheese")

# 2. There is one chair between Timothy's Mom and the one eating Stew.
cnf += one_between("timothy", "stew")

# 3. There are two chairs between the Bella's Mom and Penny's seat on the right.
cnf += two_between("bella", "penny")
cnf += right_of("penny", "bella")

# 4. There is one chair between the place setting with Roses and the one eating Spaghetti on the left.
cnf += one_between("roses", "spaghetti")
cnf += left_of("spaghetti", "roses")

# 5. There are two chairs between the place setting with Carnations and Samantha's Mom.
cnf += two_between("carnations", "samantha")

# 6. There is one chair between Meredith's Mom and Timothy's Mom on the left.
cnf += one_between("meredith", "timothy")
cnf += left_of("timothy", "meredith")

# 7. Aniya's place setting has a lovely Carnation bouquet.
cnf += same_house("aniya", "carnations")

# 8. There are two chairs between the one eating Grilled Cheese and the one eating Spaghetti.
cnf += two_between("grilled cheese", "spaghetti")

# 9. The person in the first chair (left-most) is eating Pizza.
cnf += found_at("pizza", 1)

# 10. The Tulips were placed at one of the place settings somewhere to the left of Penny's chair.
cnf += left_of("tulips", "penny")

# 11. There are two chairs between the one eating Spaghetti and Kailyn's seat.
cnf += two_between("spaghetti", "kailyn")

# 12. There is one chair between the one eating Pizza and Holly's chair on the right.
cnf += one_between("pizza", "holly")
cnf += right_of("holly", "pizza")


all_solutions = sat_utils.solve_all(cnf)
print(f"{len(all_solutions)} solutions found")
print(all_solutions)
