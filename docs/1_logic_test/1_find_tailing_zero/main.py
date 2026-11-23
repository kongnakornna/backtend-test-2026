"""
เขียบนโปรแกรมหาจำนวนเลข 0 ที่ออยู่ติดกันหลังสุดของค่า factorial โดยห้ามใช้ function from math

[Input]
number: as an integer

[Output]
count: count of tailing zero as an integer

[Example 1]
input = 7
output = 1

[Example 2]
input = -10
output = number can not be negative
"""


class Solution:

    def find_tailing_zeroes(self, number: int) -> int | str:
        # Trailing zeros come from 2x5 pairs; factorials have more 2s than 5s,
        # so count factors of 5: n//5 + n//25 + n//125 + ...  -> O(log5 n)
        if number < 0:
            return "number can not be negative"

        count = 0
        while number >= 5:
            number //= 5
            count += number
        return count
