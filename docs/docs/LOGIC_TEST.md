# Part 1 — Logic Test: แนวคิดและ edge cases

## 1) `find_tailing_zeroes` — `1_logic_test/1_find_tailing_zero/main.py`

- เลข 0 ท้ายเกิดจากคู่ `2 × 5` และใน `n!` มีตัวประกอบ 2 มากกว่า 5 เสมอ → นับตัวประกอบ 5
- สูตร `n//5 + n//25 + n//125 + ...` (เขียนเป็นลูป `n //= 5; count += n` จน `n < 5`) ไม่ต้องคำนวณ factorial จริง
- Edge cases: `n < 0` → `"number can not be negative"`, `0..4` → `0`
- Complexity: `O(log₅ n)` time, `O(1)` space

| input | output |
|---|---|
| 7 | 1 |
| 25 | 6 |
| 100 | 24 |
| -10 | number can not be negative |

## 2) `find_max_index` — `1_logic_test/2_index_of_max/main.py`

- วนครั้งเดียว เก็บ index ของค่าที่มากที่สุด ใช้ `>` (ไม่ใช่ `>=`) → ค่าซ้ำคืน index แรก
- Edge case: `[]` → `"list can not blank"`
- Complexity: `O(n)` time, `O(1)` space

## 3) `number_to_thai` — `1_logic_test/3_number_to_thai/main.py`

- แยกเป็นกลุ่ม "ล้าน" กับส่วนที่ต่ำกว่าล้าน แล้วอ่านแต่ละกลุ่มด้วยหลัก หน่วย/สิบ/ร้อย/พัน/หมื่น/แสน
- กฎพิเศษ:
  - `0` → `ศูนย์`
  - 1 ในหลักสิบ → `สิบ` (ไม่ใช่ หนึ่งสิบ)
  - 2 ในหลักสิบ → `ยี่สิบ`
  - 1 ในหลักหน่วย เมื่อมีหลักที่สูงกว่า → `เอ็ด` (รวมถึงข้ามกลุ่มล้าน เช่น 1,000,001 = หนึ่งล้านเอ็ด)
  - ศูนย์ในหลักใดก็ข้าม
- Edge cases: `< 0` → `"number can not less than 0"`, `> 10,000,000` → `"number can not more than 10000000"`

| input | output |
|---|---|
| 101 | หนึ่งร้อยเอ็ด |
| 11 | สิบเอ็ด |
| 21 | ยี่สิบเอ็ด |
| 1,000,001 | หนึ่งล้านเอ็ด |
| 2,510,021 | สองล้านห้าแสนหนึ่งหมื่นยี่สิบเอ็ด |
| 10,000,000 | สิบล้าน |

## 4) `number_to_roman` — `1_logic_test/4_number_to_roman/main.py`

- Greedy จากค่ามากไปน้อย รวม subtractive pairs:
  `1000 M, 900 CM, 500 D, 400 CD, 100 C, 90 XC, 50 L, 40 XL, 10 X, 9 IX, 5 V, 4 IV, 1 I`
- ใช้ `divmod` ต่อ symbol จึงวนแค่ 13 รอบเสมอ
- Edge cases: `< 0` → `"number can not less than 0"`, `0` → `"number can not less than 1"` (โรมันไม่มีศูนย์), `> 3999` → `"number can not more than 3999"` (เลขโรมันมาตรฐานสูงสุด MMMCMXCIX)

| input | output |
|---|---|
| 101 | CI |
| 1994 | MCMXCIV |
| 3999 | MMMCMXCIX |
