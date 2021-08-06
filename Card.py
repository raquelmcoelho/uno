from enum import Enum


class CardColor(Enum):
    RED = 0
    YELLOW = 1
    BLUE = 2
    GREEN = 3
    BLACK = 4


class CardContent(Enum):
    zero = 0
    one = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9
    revert = 10
    block = 11
    plustwo = 12
    plusfour = 13
    changecolor = 14


class Carta:
    def __init__(self, cardcolor, cardcontent):
        self.color = cardcolor.name
        self.content = cardcontent.name

    def __str__(self):
        return [str(self.color), str(self.content)]
