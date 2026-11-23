"""
เขียบนโปรแกรมแปลงตัวเลยเป็นคำอ่านภาษาไทย

[Input]
number: positive number rang from 0 to 10_000_000

[Output]
num_text: string of thai number call

[Example 1]
input = 101
output = หนึ่งร้อยเอ็ด

[Example 2]
input = -1
output = number can not less than 0
"""


class Solution:

    DIGITS = ["", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    UNITS = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน"]
    MAX_NUMBER = 10_000_000

    def number_to_thai(self, number: int) -> str:
        if number < 0:
            return "number can not less than 0"
        if number > self.MAX_NUMBER:
            return "number can not more than 10000000"
        if number == 0:
            return "ศูนย์"

        millions, rest = divmod(number, 1_000_000)
        text = ""
        if millions:
            text += self._read_below_million(millions) + "ล้าน"
        if rest:
            text += self._read_below_million(rest, has_higher=bool(millions))
        return text

    def _read_below_million(self, number: int, has_higher: bool = False) -> str:
        """Read 1..999_999. has_higher: a higher group exists (e.g. ล้าน) so a lone 1 is เอ็ด."""
        digits = str(number)
        size = len(digits)
        text = ""
        for i, char in enumerate(digits):
            digit = int(char)
            position = size - i - 1  # 0 = units, 1 = tens, ...
            if digit == 0:
                continue
            if position == 0 and digit == 1 and (size > 1 or has_higher):
                text += "เอ็ด"
            elif position == 1 and digit == 1:
                text += "สิบ"
            elif position == 1 and digit == 2:
                text += "ยี่สิบ"
            else:
                text += self.DIGITS[digit] + self.UNITS[position]
        return text
