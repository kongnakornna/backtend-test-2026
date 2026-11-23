## Question
![](/assets/q_idempotency.png)
## Response Section

### ความหมาย

**Idempotency** คือคุณสมบัติที่การส่ง request เดียวกัน **ซ้ำกี่ครั้งก็ได้** แล้ว **สถานะของระบบ (server state) ต้องเหมือนกับการส่งเพียงครั้งเดียว**
(response อาจต่างได้ เช่น `DELETE` ครั้งแรกได้ `204` ครั้งที่สองได้ `404` แต่ข้อมูลในระบบเหมือนเดิม)

ทำไมสำคัญ: ใน network จริง client ไม่รู้ว่า request ที่ timeout นั้น "ไปถึง server แล้วหรือยัง" จึงต้อง **retry**
ถ้า API ไม่ idempotent → การ retry อาจทำให้ **ตัดเงินซ้ำ, สร้าง order ซ้ำ, ส่ง email ซ้ำ**

### HTTP methods

| Method | Safe (ไม่เปลี่ยนข้อมูล) | Idempotent | เหตุผล |
|---|:---:|:---:|---|
| `GET`, `HEAD`, `OPTIONS` | ✅ | ✅ | อ่านอย่างเดียว |
| `PUT` | ❌ | ✅ | แทนที่ resource ทั้งก้อนด้วยค่าเดิม → ผลเหมือนเดิม |
| `DELETE` | ❌ | ✅ | ลบแล้วก็คือไม่มี ลบซ้ำก็ยังไม่มี |
| `PATCH` | ❌ | ⚠️ ขึ้นกับการออกแบบ | `{"name": "A"}` idempotent แต่ `{"op": "increment"}` ไม่ใช่ |
| `POST` | ❌ | ❌ | สร้าง resource ใหม่ทุกครั้ง → **ต้องออกแบบเพิ่มเอง** |

### วิธีทำ POST ให้ idempotent: `Idempotency-Key`

1. Client สร้าง key เฉพาะ (UUID) ต่อ 1 operation แล้วส่งใน header `Idempotency-Key` — ถ้า retry ต้องใช้ **key เดิม**
2. Server เก็บ key + hash ของ request + response ไว้ใน DB โดยให้ key เป็น **UNIQUE**
3. ถ้า key เคยประมวลผลสำเร็จแล้ว → คืน **response เดิม** โดยไม่ทำซ้ำ
4. ถ้า key เดิมแต่ payload ต่างกัน → `422` / `409` (client ใช้ key ผิด)
5. ถ้า key เดิมกำลังประมวลผลอยู่ (request ซ้อนกัน) → `409 Conflict` ให้ client retry ภายหลัง
6. ลบ key เก่าตาม TTL (เช่น 24 ชั่วโมง)

### ตัวอย่าง implement ด้วย Python (Django REST Framework)

```python
# models.py
import uuid
from django.db import models


class IdempotencyRecord(models.Model):
    key = models.CharField(max_length=255, unique=True)       # UNIQUE กันการประมวลผลซ้ำ
    request_hash = models.CharField(max_length=64)
    status_code = models.PositiveSmallIntegerField(null=True)  # null = กำลังประมวลผล
    response_body = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    order_id = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
```

```python
# views.py
import hashlib
import json

from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IdempotencyRecord, Payment


def hash_payload(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class PaymentView(APIView):
    def post(self, request):
        key = request.headers.get("Idempotency-Key")
        if not key:
            return Response({"detail": "Idempotency-Key header is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        request_hash = hash_payload(request.data)

        # 1) จอง key — UNIQUE constraint ทำให้มีเพียง request เดียวที่จองสำเร็จ (กัน race condition)
        try:
            with transaction.atomic():
                record = IdempotencyRecord.objects.create(key=key, request_hash=request_hash)
        except IntegrityError:
            record = IdempotencyRecord.objects.get(key=key)
            if record.request_hash != request_hash:
                return Response({"detail": "Idempotency-Key reused with a different payload."},
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            if record.status_code is None:
                return Response({"detail": "Request with this key is still being processed."},
                                status=status.HTTP_409_CONFLICT)
            # 2) เคยทำสำเร็จแล้ว -> คืนผลลัพธ์เดิม ไม่สร้าง payment ซ้ำ
            return Response(record.response_body, status=record.status_code)

        # 3) ทำงานจริง + บันทึก response ใน transaction เดียวกัน
        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    order_id=request.data["order_id"],
                    amount=request.data["amount"],
                )
                body = {"id": payment.id, "order_id": payment.order_id, "amount": str(payment.amount)}
                record.status_code = status.HTTP_201_CREATED
                record.response_body = body
                record.save(update_fields=["status_code", "response_body"])
        except Exception:
            record.delete()  # ล้มเหลว -> ปล่อย key ให้ client retry ได้
            raise

        return Response(body, status=status.HTTP_201_CREATED)
```

ผลลัพธ์:

```text
POST /payments  Idempotency-Key: 7f3c...  {"order_id": "A1", "amount": "100"}  -> 201 {"id": 1, ...}
POST /payments  Idempotency-Key: 7f3c...  {"order_id": "A1", "amount": "100"}  -> 201 {"id": 1, ...}  (ไม่สร้างใหม่)
POST /payments  Idempotency-Key: 7f3c...  {"order_id": "A1", "amount": "999"}  -> 422
```

### เทคนิคอื่นที่ช่วยให้ idempotent

- ใช้ `PUT /resources/{client_generated_id}` แทน `POST` เมื่อ client กำหนด id ได้
- ใช้ **unique constraint ทาง business** เช่น `UNIQUE(order_id)` ในตาราง payment
- ใช้ `update_or_create()` / `INSERT ... ON CONFLICT DO NOTHING`
- อัปเดตแบบ "set ค่า" (`status = 'paid'`) แทน "เพิ่มค่า" (`balance += 100`)
- ฝั่ง consumer ของ message queue: เก็บ `message_id` ที่ประมวลผลแล้ว เพื่อรองรับ at-least-once delivery
