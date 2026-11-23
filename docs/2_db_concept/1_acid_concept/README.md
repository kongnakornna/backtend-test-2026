## Question
![](/assets/q_acid.png)
## Response Section

ACID คือคุณสมบัติ 4 ข้อของ **transaction** ในฐานข้อมูล (โดยเฉพาะ relational DB) ที่รับประกันว่าข้อมูลจะถูกต้องและเชื่อถือได้ แม้มีการทำงานพร้อมกันหรือระบบล่ม

### 1. ความหมายของตัวอักษร A, C, I, D

| ตัวอักษร | ชื่อ | ความหมาย | ตัวอย่าง |
|---|---|---|---|
| **A** | Atomicity | transaction ต้อง "สำเร็จทั้งหมด หรือไม่เกิดขึ้นเลย" ถ้าขั้นตอนใดล้มเหลว ต้อง rollback ทั้งก้อน | โอนเงิน A → B: ถ้าหักเงิน A แล้วเพิ่มเงิน B ไม่สำเร็จ ต้องคืนเงิน A ด้วย |
| **C** | Consistency | transaction ต้องพาข้อมูลจากสถานะที่ถูกต้อง ไปสู่สถานะที่ถูกต้อง ไม่ละเมิด constraint/กฎ | FK ต้องชี้ไปแถวที่มีอยู่จริง, `balance >= 0`, email ต้อง unique |
| **I** | Isolation | transaction ที่ทำงานพร้อมกันต้องไม่เห็น/ไม่รบกวนข้อมูลที่ยังไม่ commit ของกันและกัน ผลลัพธ์ต้องเหมือนทำทีละรายการ (ตามระดับ isolation) | 2 request ซื้อสินค้าชิ้นสุดท้ายพร้อมกัน ต้องขายได้แค่ชิ้นเดียว |
| **D** | Durability | เมื่อ commit แล้ว ข้อมูลต้องไม่หาย แม้ไฟดับหรือ server crash | DB เขียน Write-Ahead Log (WAL) ลง disk ก่อนตอบว่า commit สำเร็จ |

ระดับ Isolation (จากต่ำไปสูง): `Read Uncommitted` → `Read Committed` → `Repeatable Read` → `Serializable`
ยิ่งสูงยิ่งป้องกัน dirty read / non-repeatable read / phantom read / lost update ได้มากขึ้น แต่แลกกับ concurrency และ performance ที่ลดลง

### 2. ฝั่งฐานข้อมูล vs ฝั่งแอปพลิเคชัน รับผิดชอบอะไร

| คุณสมบัติ | ฝั่งฐานข้อมูลรับผิดชอบ | ฝั่งแอปพลิเคชันต้องรับผิดชอบ |
|---|---|---|
| **Atomicity** | กลไก `BEGIN / COMMIT / ROLLBACK`, undo log, rollback อัตโนมัติเมื่อเกิด error | **กำหนดขอบเขต transaction ให้ถูก** — รวมคำสั่งที่ต้องสำเร็จด้วยกันไว้ใน transaction เดียว (เช่น `transaction.atomic()` ใน Django), จัดการ exception ให้ rollback, ไม่เรียก external side effect (ส่ง email, เรียก payment API) ภายใน transaction โดยไม่มีแผนชดเชย (เช่น outbox pattern / saga) |
| **Consistency** | บังคับ constraint ที่ประกาศไว้: `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `NOT NULL`, `CHECK`, trigger | **ออกแบบ schema/constraint ให้ครบ** และ **validate business rule** ที่ DB ไม่รู้ เช่น "ครูต้องสอนห้องที่อยู่โรงเรียนเดียวกัน", "ห้ามจองเกินจำนวนที่นั่ง" — DB รับประกัน consistency ได้เฉพาะกฎที่ถูกบอกไว้เท่านั้น |
| **Isolation** | locking / MVCC, การ implement isolation level แต่ละระดับ, ตรวจจับ deadlock / serialization failure | **เลือก isolation level ให้เหมาะกับงาน**, ใช้ `SELECT ... FOR UPDATE` (`select_for_update()`) หรือ optimistic locking (version column) เมื่อมี read-modify-write, ใช้ `F()` expression แทนการอ่านมาบวกใน Python, **retry** เมื่อเจอ deadlock/serialization error, ทำ transaction ให้สั้น |
| **Durability** | WAL / redo log, `fsync` ลง disk, crash recovery, replication | ตั้งค่า infra ให้เหมาะสม (ไม่ปิด `fsync`, ตั้ง `synchronous_commit`), ทำ **backup + ทดสอบ restore**, replication/HA, และถือว่าข้อมูลบันทึกแล้วก็ต่อเมื่อได้รับผล commit สำเร็จเท่านั้น |

**สรุป:** ฐานข้อมูลให้ "เครื่องมือ" ของ ACID มา แต่แอปพลิเคชันต้อง "ใช้เครื่องมือให้ถูก" —
กำหนดขอบเขต transaction, ประกาศ constraint, เลือก isolation/locking และจัดการ error/retry
ถ้าแอปเขียนผิด (เช่น อ่านค่ามาคำนวณใน Python แล้วเขียนกลับโดยไม่ lock) ต่อให้ DB รองรับ ACID ข้อมูลก็ยังผิดได้

ตัวอย่างใน Django:

```python
from django.db import transaction
from django.db.models import F

def transfer(from_id: int, to_id: int, amount: Decimal) -> None:
    with transaction.atomic():                                   # Atomicity
        src = Account.objects.select_for_update().get(pk=from_id)  # Isolation
        if src.balance < amount:                                  # Consistency (business rule)
            raise InsufficientBalance()
        Account.objects.filter(pk=from_id).update(balance=F("balance") - amount)
        Account.objects.filter(pk=to_id).update(balance=F("balance") + amount)
    # หลังออกจาก block = COMMIT แล้ว -> Durability โดย DB
```
