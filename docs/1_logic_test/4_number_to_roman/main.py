"""
เขียบนโปรแกรมแปลงตัวเลยเป็นตัวเลข roman

[Input]
number: list of numbers

[Output]
roman_text: roman number

[Example 1]
input = 101
output = CI

[Example 2]
input = -1
output = number can not less than 0
"""


class Solution:

    ROMAN_MAP = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    def number_to_roman(self, number: int) -> str:
        # Greedy from largest symbol to smallest. Standard roman numerals
        # have no zero and top out at 3999 (MMMCMXCIX).
        if number < 0:
            return "number can not less than 0"
        if number == 0:
            return "number can not less than 1"
        if number > 3999:
            return "number can not more than 3999"

        result = []
        for value, symbol in self.ROMAN_MAP:
            count, number = divmod(number, value)
            result.append(symbol * count)
        return "".join(result)
