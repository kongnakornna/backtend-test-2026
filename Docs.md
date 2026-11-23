# Backend Exam — คำตอบ และคู่มือการใช้งาน

เอกสารนี้มี 2 ส่วน

1. **คำตอบตามโจทย์** ข้อ 1–4 (ACID, JSON vs Protobuf, Idempotency, Database indexing)
2. **คู่มือการใช้งาน** School API ทั้ง 2 เวอร์ชัน: Django REST Framework (`docs/4_rest_api`) และ FastAPI + DDD (`fastapi-ddd-school`)

> คำตอบฉบับเต็ม (ตาราง/ตัวอย่างละเอียดกว่านี้) อยู่ที่
> `docs/2_db_concept/1_acid_concept/README.md`, `docs/2_db_concept/2_index_concept/README.md`,
> `docs/3_api_concept/1_idempotency/README.md`, `docs/3_api_concept/2_data_format/README.md`

---

# ส่วนที่ 1 — คำตอบตามโจทย์

## ข้อ 1 — ACID

> อธิบายความหมายของ ACID ในบริบทของการพัฒนาระบบหลังบ้าน
> * ความหมายของตัวอักษร A, C, I, D
> * ฝั่งฐานข้อมูลรับผิดชอบเรื่องใด และฝั่งแอปพลิเคชันต้องรับผิดชอบเรื่องใด

ACID คือคุณสมบัติ 4 ข้อของ **transaction** ที่รับประกันว่าข้อมูลถูกต้องและเชื่อถือได้ แม้มีการทำงานพร้อมกันหรือระบบล่ม

### 1.1 ความหมาย

| | ชื่อ | ความหมาย | ตัวอย่าง |
|---|---|---|---|
| **A** | Atomicity | สำเร็จทั้งหมด หรือไม่เกิดขึ้นเลย ถ้าขั้นใดล้มเหลวต้อง rollback ทั้งก้อน | โอนเงิน A→B: หัก A แล้วเพิ่ม B ไม่สำเร็จ ต้องคืนเงิน A |
| **C** | Consistency | พาข้อมูลจากสถานะที่ถูกต้องไปสู่สถานะที่ถูกต้อง ไม่ละเมิด constraint | FK ต้องชี้แถวที่มีจริง, `balance >= 0`, email unique |
| **I** | Isolation | transaction ที่ทำพร้อมกันไม่เห็นข้อมูลที่ยังไม่ commit ของกัน ผลเหมือนทำทีละรายการ (ตาม isolation level) | 2 request ซื้อสินค้าชิ้นสุดท้ายพร้อมกัน ต้องขายได้ชิ้นเดียว |
| **D** | Durability | commit แล้วข้อมูลไม่หาย แม้ไฟดับหรือ crash | DB เขียน WAL ลง disk ก่อนตอบว่า commit สำเร็จ |

Isolation level จากต่ำไปสูง: `Read Uncommitted` → `Read Committed` → `Repeatable Read` → `Serializable`
ยิ่งสูงยิ่งกัน dirty read / non-repeatable read / phantom read / lost update ได้มาก แต่ concurrency ลดลง

### 1.2 ฐานข้อมูล vs แอปพลิเคชัน

| | ฐานข้อมูลรับผิดชอบ | แอปพลิเคชันต้องรับผิดชอบ |
|---|---|---|
| **A** | `BEGIN / COMMIT / ROLLBACK`, undo log, rollback เมื่อ error | กำหนดขอบเขต transaction ให้ถูก (`transaction.atomic()`, Unit of Work), จัดการ exception, ไม่เรียก side effect ภายนอก (email, payment API) ใน transaction โดยไม่มีแผนชดเชย (outbox / saga) |
| **C** | บังคับ PK, FK, UNIQUE, NOT NULL, CHECK, trigger | ออกแบบ constraint ให้ครบ และ validate business rule ที่ DB ไม่รู้ เช่น "ครูสอนได้เฉพาะห้องในโรงเรียนตัวเอง" |
| **I** | locking / MVCC, implement isolation level, ตรวจ deadlock | เลือก isolation level, ใช้ `SELECT ... FOR UPDATE` หรือ optimistic lock (version column) เมื่อ read-modify-write, ใช้ `F()` / `UPDATE x = x + 1` แทนการบวกใน Python, retry เมื่อเจอ deadlock/serialization error, ทำ transaction ให้สั้น |
| **D** | WAL / redo log, `fsync`, crash recovery, replication | ตั้งค่า infra ให้ถูก (ไม่ปิด `fsync`), backup + ทดสอบ restore, HA, ถือว่าบันทึกแล้วเมื่อได้ผล commit สำเร็จเท่านั้น |

**สรุป:** DB ให้ "เครื่องมือ" ของ ACID แต่แอปต้อง "ใช้ให้ถูก" — ถ้าอ่านค่ามาคำนวณใน Python แล้วเขียนกลับโดยไม่ lock ต่อให้ DB รองรับ ACID ข้อมูลก็ผิดได้

---

## ข้อ 2 — JSON vs Protocol Buffers

> เปรียบเทียบความแตกต่างของ JSON กับ Protocol Buffer พร้อมอธิบายข้อดีและข้อเสียของแต่ละรูปแบบ

### 2.1 ความแตกต่าง

| | JSON | Protocol Buffers |
|---|---|---|
| รูปแบบ | Text (UTF-8) อ่านด้วยตาได้ | Binary อ่านด้วยตาไม่ได้ |
| Schema | ไม่บังคับ (เสริมด้วย JSON Schema / OpenAPI) | บังคับ ประกาศใน `.proto` |
| Type | string, number, boolean, null, array, object | int32/int64, float/double, bool, string, bytes, enum, message, repeated, map, oneof |
| ขนาด | ใหญ่ (ชื่อ field ซ้ำทุก record) | เล็กกว่าราว 3–10 เท่า (field number + varint) |
| ความเร็ว | parse text ช้ากว่า | decode binary เร็วกว่า |
| Code generation | ไม่ต้อง | ต้องใช้ `protoc` |
| Browser | native (`JSON.parse`) | ต้องใช้ library / gRPC-Web |
| ใช้กับ | REST, public API, frontend ↔ backend, config | gRPC, microservice ภายใน, mobile/IoT, event streaming |

```proto
syntax = "proto3";
message Student {
  int64 id = 1;
  string first_name = 2;
  repeated int64 classroom_ids = 3;
}
```

```python
import json
from student_pb2 import Student            # protoc --python_out=. student.proto

json.dumps({"id": 1, "first_name": "Somchai", "classroom_ids": [10, 11]})   # text
raw = Student(id=1, first_name="Somchai", classroom_ids=[10, 11]).SerializeToString()  # bytes
Student.FromString(raw)
```

### 2.2 JSON

**ข้อดี:** อ่าน/debug ง่าย (log, curl, DevTools) · ทุกภาษาและ browser รองรับ · ไม่ต้องมี schema/compile เริ่มได้เร็ว · ecosystem ใหญ่ (OpenAPI, Postman) · เหมาะกับ public API

**ข้อเสีย:** payload ใหญ่ · parse ช้า ใช้ CPU มาก · type จำกัด (ไม่มี int/float แยก, ไม่มี date/decimal/binary ต้องตกลงรูปแบบเอง) · เลขเกิน 2^53 เสียความแม่นยำใน JavaScript · ไม่มี schema บังคับ ต้อง validate เอง

### 2.3 Protocol Buffers

**ข้อดี:** เล็กและเร็ว · strongly typed, schema เป็น contract, generate code หลายภาษา · backward/forward compatible ถ้าทำตามกฎ (เพิ่ม field ใหม่ได้ client เก่า ignore) · เป็นพื้นฐานของ gRPC (HTTP/2, streaming)

**ข้อเสีย:** debug ยาก ต้องมี `.proto` ช่วย decode · ต้องมี build step และจัดการ version `.proto` ระหว่างทีม · browser ไม่รองรับ native · ห้ามเปลี่ยน/ใช้ field number ซ้ำ (ใช้ `reserved`) · proto3 แยก "ไม่ได้ส่ง" กับค่า default ไม่ได้ถ้าไม่ใช้ `optional` · tooling สำหรับ public API น้อยกว่า

**เลือกใช้:** JSON สำหรับ public REST / web / third-party · Protobuf สำหรับ service-to-service ภายใน, throughput สูง, mobile ที่ต้องประหยัด bandwidth — หลายระบบใช้ทั้งคู่ (JSON ที่ gateway, gRPC ภายใน)

---

## ข้อ 3 — Idempotency

> อธิบายความหมายของ Idempotency ในบริบทของการพัฒนา RESTful API พร้อมยกตัวอย่างการ implement ด้วย code ภาษา Python

### 3.1 ความหมาย

**Idempotency** คือการส่ง request เดียวกันซ้ำกี่ครั้งก็ได้ แล้ว **สถานะของระบบเหมือนกับส่งครั้งเดียว** (response อาจต่างได้ เช่น `DELETE` ครั้งแรก `204` ครั้งที่สอง `404`)

สำคัญเพราะ client ไม่รู้ว่า request ที่ timeout ไปถึง server แล้วหรือยัง จึงต้อง retry — ถ้า API ไม่ idempotent จะ **ตัดเงินซ้ำ / สร้าง order ซ้ำ**

| Method | Safe | Idempotent | เหตุผล |
|---|:---:|:---:|---|
| `GET`, `HEAD`, `OPTIONS` | ✅ | ✅ | อ่านอย่างเดียว |
| `PUT` | ❌ | ✅ | แทนที่ทั้งก้อนด้วยค่าเดิม ผลเหมือนเดิม |
| `DELETE` | ❌ | ✅ | ลบซ้ำก็ยังไม่มี |
| `PATCH` | ❌ | ⚠️ | `{"name": "A"}` ใช่ แต่ `{"op": "increment"}` ไม่ใช่ |
| `POST` | ❌ | ❌ | สร้างใหม่ทุกครั้ง ต้องออกแบบเพิ่ม |

### 3.2 ทำ POST ให้ idempotent ด้วย `Idempotency-Key`

1. Client สร้าง UUID ต่อ 1 operation ส่งใน header `Idempotency-Key` — retry ใช้ key เดิม
2. Server เก็บ key (UNIQUE) + hash ของ request + response
3. key เคยสำเร็จแล้ว → คืน response เดิม ไม่ทำซ้ำ
4. key เดิมแต่ payload ต่าง → `422`
5. key เดิมกำลังประมวลผล → `409` ให้ retry ภายหลัง
6. ลบ key เก่าตาม TTL (เช่น 24 ชม.)

### 3.3 ตัวอย่าง Python (FastAPI + SQLAlchemy async)

```python
import hashlib, json
from decimal import Decimal

from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import JSON, String, Integer, Numeric, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...

class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    key: Mapped[str] = mapped_column(String(255), primary_key=True)   # UNIQUE กันทำซ้ำ
    request_hash: Mapped[str] = mapped_column(String(64))
    status_code: Mapped[int | None] = mapped_column(Integer)          # None = กำลังประมวลผล
    response_body: Mapped[dict | None] = mapped_column(JSON)

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))


class PaymentIn(BaseModel):
    order_id: str
    amount: Decimal

app = FastAPI()

async def get_session() -> AsyncSession: ...   # async_sessionmaker() ของโปรเจกต์


@app.post("/payments", status_code=201)
async def create_payment(
    body: PaymentIn,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
):
    request_hash = hashlib.sha256(body.model_dump_json().encode()).hexdigest()

    # 1) จอง key — PK/UNIQUE ทำให้มีเพียง request เดียวที่จองได้ (กัน race condition)
    try:
        session.add(IdempotencyRecord(key=idempotency_key, request_hash=request_hash))
        await session.commit()
    except IntegrityError:
        await session.rollback()
        record = await session.get(IdempotencyRecord, idempotency_key)
        if record.request_hash != request_hash:
            raise HTTPException(422, "Idempotency-Key reused with a different payload")
        if record.status_code is None:
            raise HTTPException(409, "Request with this key is still being processed")
        return record.response_body          # 2) เคยทำแล้ว → คืนผลเดิม ไม่สร้าง payment ซ้ำ

    # 3) ทำงานจริง + บันทึก response ใน transaction เดียวกัน
    try:
        payment = Payment(order_id=body.order_id, amount=body.amount)
        session.add(payment)
        await session.flush()
        result = {"id": payment.id, "order_id": payment.order_id, "amount": str(payment.amount)}
        record = await session.get(IdempotencyRecord, idempotency_key)
        record.status_code, record.response_body = 201, result
        await session.commit()
    except Exception:
        await session.rollback()
        record = await session.get(IdempotencyRecord, idempotency_key)
        await session.delete(record)         # ล้มเหลว → ปล่อย key ให้ client retry ได้
        await session.commit()
        raise
    return result
```

```text
POST /payments  Idempotency-Key: 7f3c…  {"order_id":"A1","amount":"100"}  → 201 {"id":1,…}
POST /payments  Idempotency-Key: 7f3c…  {"order_id":"A1","amount":"100"}  → 201 {"id":1,…}  (ไม่สร้างใหม่)
POST /payments  Idempotency-Key: 7f3c…  {"order_id":"A1","amount":"999"}  → 422
```

(ตัวอย่างฉบับ Django REST Framework อยู่ใน `docs/3_api_concept/1_idempotency/README.md`)

**เทคนิคอื่น:** `PUT /resources/{client_id}` แทน POST · unique constraint ทาง business (`UNIQUE(order_id)`) · `INSERT ... ON CONFLICT DO NOTHING` / `update_or_create()` · อัปเดตแบบ set ค่า (`status='paid'`) แทนเพิ่มค่า (`balance += 100`) · consumer ของ queue เก็บ `message_id` ที่ประมวลผลแล้ว (at-least-once delivery)

---

## ข้อ 4 — Database Indexing

> อธิบายข้อดีและข้อจำกัดของการทำ Database indexing

**Index** คือโครงสร้างข้อมูลเสริม (ส่วนใหญ่เป็น B-Tree/B+Tree, หรือ Hash, GIN, GiST, BRIN) ที่เก็บค่าคอลัมน์แบบเรียงลำดับพร้อม pointer ไปยังแถวจริง — เหมือนสารบัญท้ายหนังสือ ค้นจาก `O(n)` (full scan) เหลือ `O(log n)`

### ข้อดี

1. **ค้นหาเร็วขึ้นมาก** — `WHERE`, lookup ด้วย PK/FK
2. **ช่วย `ORDER BY` / `GROUP BY` / `MIN` / `MAX`** — เรียงไว้แล้ว ไม่ต้อง sort ใหม่
3. **บังคับความถูกต้อง** — `UNIQUE` index กันข้อมูลซ้ำ
4. **Covering index / index-only scan** — ไม่ต้องอ่าน table เลยถ้า index มีครบทุกคอลัมน์ที่ใช้
5. **JOIN เร็วขึ้น** — index บน FK
6. **ลด I/O และ lock** — อ่านเฉพาะ page ที่จำเป็น รองรับ concurrency ได้ดีขึ้น

### ข้อจำกัด

1. **เขียนช้าลง** — ทุก `INSERT/UPDATE/DELETE` ต้องอัปเดตทุก index (write amplification)
2. **ใช้พื้นที่ disk และ memory เพิ่ม** — บางครั้ง index รวมกันใหญ่กว่า table
3. **ไม่ช่วยทุก query**
   - คอลัมน์ selectivity ต่ำ (gender, boolean) → planner มักเลือก full scan
   - ใช้ function กับคอลัมน์ (`LOWER(email) = ...`) → ต้องใช้ expression index
   - `LIKE '%abc'` ใช้ B-Tree ไม่ได้ → ต้องใช้ trigram / full-text
   - type ไม่ตรงจน implicit cast → index ไม่ถูกใช้
4. **Composite index ขึ้นกับลำดับคอลัมน์ (leftmost prefix)** — `(school_id, last_name)` ช่วย `WHERE school_id = ?` แต่ไม่ช่วย `WHERE last_name = ?` อย่างเดียว
5. **ต้องดูแล** — bloat/fragmentation, statistics ล้าสมัย ต้อง `ANALYZE` / `REINDEX`
6. **สร้าง index บน table ใหญ่อาจ lock** — production ใช้ `CREATE INDEX CONCURRENTLY` (PostgreSQL)
7. **Index ซ้ำซ้อน/ไม่ถูกใช้** — เปลืองทรัพยากรเปล่า ๆ

**สรุป:** index คือการแลกพื้นที่และความเร็วในการเขียน เพื่อความเร็วในการอ่าน — ออกแบบจาก query จริงและตรวจด้วย `EXPLAIN ANALYZE` เสมอ

---

# ส่วนที่ 2 — คู่มือการใช้งาน School API

ระบบจัดการ **โรงเรียน · ห้องเรียน · ครู · นักเรียน** มี 2 implementation ที่ requirement เดียวกัน

| | Django REST Framework | FastAPI + DDD |
|---|---|---|
| ที่อยู่ | `docs/4_rest_api/` | `fastapi-ddd-school/` |
| Python | 3.10–3.12 | 3.11+ (ใช้ `uv`) |
| DB | SQLite | SQLite (default) / PostgreSQL |
| Auth | ต้อง login (Basic / Session) | ไม่มี |
| URL | มี `/` ท้าย เช่น `/api/v1/schools/` | ไม่มี `/` ท้าย เช่น `/api/v1/schools` |
| เอกสาร API | Browsable API ที่ `/api/v1/` | Swagger ที่ `/docs` |
| Tests | `python manage.py test apis` (44) | `uv run pytest` (70) |

## Data model

```mermaid
erDiagram
    SCHOOL ||--o{ CLASSROOM : has
    SCHOOL ||--o{ TEACHER : employs
    CLASSROOM ||--o{ STUDENT : contains
    TEACHER }o--o{ CLASSROOM : teaches

    SCHOOL { int id string name string abbreviation text address }
    CLASSROOM { int id int school_id int year_level string section }
    TEACHER { int id int school_id string first_name string last_name string gender }
    STUDENT { int id int classroom_id string first_name string last_name string gender }
```

- ครู M:N ห้องเรียน, นักเรียน N:1 ห้องเรียน
- ครูมี `school` ของตัวเอง เพื่อ filter/นับครูตามโรงเรียนได้แม้ยังไม่ผูกห้อง
- `gender`: `M`, `F`, `O`
- `(school, year_level, section)` ห้ามซ้ำ — ห้อง 1/1 มีได้ห้องเดียวต่อโรงเรียน
- `year_level >= 1`

## Business rules (ทั้ง 2 เวอร์ชัน)

- ครูผูกได้เฉพาะห้องเรียนในโรงเรียนเดียวกับครู — ตรวจตอนสร้าง, เปลี่ยนห้อง และเปลี่ยนโรงเรียน
- ห้ามย้ายห้องเรียนไปโรงเรียนอื่น ถ้ายังมีครูของโรงเรียนเดิมผูกอยู่

---

## A. Django REST Framework (`docs/4_rest_api`)

### A.1 ติดตั้งและรัน

> Django 5.0 รองรับ Python 3.10–3.12 (Python 3.14 จะ error ตอนรัน test)

```powershell
cd C:\github\backtend-test-2026\docs
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r 4_rest_api\requirements.txt

cd 4_rest_api
python manage.py migrate
python manage.py createsuperuser      # สร้าง user สำหรับเรียก API
python manage.py runserver            # http://127.0.0.1:8000/api/v1/
```

รัน test: `python manage.py test apis`

ทางลัดถ้ามี `uv` (ไม่ต้องสร้าง venv เอง):

```powershell
uv run --no-project --python 3.12 --with-requirements requirements.txt python manage.py runserver
```

### A.2 การ login

ทุก endpoint ต้อง login (`IsAuthenticated`) ไม่งั้นได้ `401`

- **Browser:** เปิด `http://127.0.0.1:8000/admin/` login ด้วย superuser แล้วเข้า `/api/v1/` (Session auth)
- **curl / Postman:** ใช้ Basic Auth

```bash
curl -u admin:password http://127.0.0.1:8000/api/v1/schools/
```

### A.3 Endpoints

| Resource | List / Create | Retrieve / Update / Delete | Filters | Detail เพิ่ม |
|---|---|---|---|---|
| School | `/api/v1/schools/` | `/api/v1/schools/{id}/` | `name` | `classroom_count`, `teacher_count`, `student_count` |
| Classroom | `/api/v1/classrooms/` | `/api/v1/classrooms/{id}/` | `school` | `school` (nested), `teachers`, `students` |
| Teacher | `/api/v1/teachers/` | `/api/v1/teachers/{id}/` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classrooms` (nested) |
| Student | `/api/v1/students/` | `/api/v1/students/{id}/` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classroom` (nested) |

- Pagination: 20 รายการต่อหน้า, `?page=2` → ตอบ `{"count", "next", "previous", "results"}`
- `name`, `firstname`, `lastname` = contains ไม่สนตัวพิมพ์; `school`, `classroom`, `gender` = ตรงตัว
- Body ใช้ `school`, `classroom`, `classrooms` (เป็น id)

### A.4 ตัวอย่างใช้งานตั้งแต่ต้น

```bash
BASE=http://127.0.0.1:8000/api/v1
AUTH="-u admin:password"
JSON="-H Content-Type:application/json"

# 1) สร้างโรงเรียน
curl $AUTH $JSON -X POST $BASE/schools/ -d '{"name":"Satit Demo","abbreviation":"SD","address":"Bangkok"}'
# 2) สร้างห้อง ม.1/1
curl $AUTH $JSON -X POST $BASE/classrooms/ -d '{"school":1,"year_level":1,"section":"1"}'
# 3) สร้างครูและผูกห้อง
curl $AUTH $JSON -X POST $BASE/teachers/ -d '{"school":1,"first_name":"Somchai","last_name":"Jaidee","gender":"M","classrooms":[1]}'
# 4) สร้างนักเรียน
curl $AUTH $JSON -X POST $BASE/students/ -d '{"classroom":1,"first_name":"Mana","last_name":"Dekdee","gender":"M"}'

# ค้นหา / ดูรายละเอียด
curl $AUTH "$BASE/teachers/?school=1&gender=M&firstname=som"
curl $AUTH "$BASE/schools/1/"          # มีจำนวนห้อง/ครู/นักเรียน
curl $AUTH "$BASE/classrooms/1/"       # มีรายชื่อครูและนักเรียน

# แก้ไข / ลบ
curl $AUTH $JSON -X PATCH $BASE/students/1/ -d '{"last_name":"Rakrian"}'
curl $AUTH -X DELETE $BASE/students/1/
```

### A.5 Status codes

| Code | เมื่อไร |
|---|---|
| `201` / `200` / `204` | create / read-update / delete |
| `400` | ข้อมูลไม่ถูกต้อง หรือผิด business rule เช่น `{"classrooms": ["Classrooms [3] do not belong to the teacher's school."]}` |
| `401` | ไม่ได้ login |
| `404` | ไม่พบ id |

---

## B. FastAPI + DDD (`fastapi-ddd-school`)

### B.1 ติดตั้งและรัน (SQLite)

ต้องมี [uv](https://docs.astral.sh/uv/) และ Python 3.11+

```powershell
cd C:\github\backtend-test-2026\fastapi-ddd-school
uv sync                                 # สร้าง .venv + ติดตั้ง dependencies
copy .env.example .env                  # ค่า default ใช้ SQLite
uv run alembic upgrade head             # สร้างตาราง
uv run uvicorn src.main:app --reload    # http://127.0.0.1:8000/docs
```

รัน test: `uv run pytest` (unit + integration, ใช้ SQLite in-memory ไม่ยุ่งกับ `school.db`)

### B.2 ใช้ PostgreSQL / Docker

```powershell
docker compose up -d db
# แก้ .env: DATABASE_URL=postgresql+asyncpg://school:school@localhost:5432/school
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

หรือรันทั้งระบบใน Docker: `docker compose up --build` (รัน migration ให้อัตโนมัติ, API ที่ port 8000)

| Env | Default | |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./school.db` | `sqlite+aiosqlite` หรือ `postgresql+asyncpg` |
| `SQL_ECHO` | `false` | แสดง SQL ใน log |
| `LOG_LEVEL` | `INFO` | |

หลังแก้ model: `uv run alembic revision --autogenerate -m "describe change"` แล้ว `uv run alembic upgrade head`

### B.3 Endpoints

| Resource | List / Create | Get / PUT / PATCH / DELETE | Filters | Detail เพิ่ม |
|---|---|---|---|---|
| School | `/api/v1/schools` | `/api/v1/schools/{id}` | `name` | `classroom_count`, `teacher_count`, `student_count` |
| Classroom | `/api/v1/classrooms` | `/api/v1/classrooms/{id}` | `school` | `teachers`, `students` |
| Teacher | `/api/v1/teachers` | `/api/v1/teachers/{id}` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classrooms` |
| Student | `/api/v1/students` | `/api/v1/students/{id}` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classroom` |

- Pagination: `?page=1&page_size=20` (สูงสุด 100) → ตอบ `{"items", "total", "page", "page_size"}`
- Body ใช้ `school_id`, `classroom_id`, `classroom_ids`
- `PUT` ต้องส่งครบทุก field, `PATCH` ส่งเฉพาะที่แก้ (ส่ง `null` = `422`)
- ลบ school → ลบห้อง/ครู/นักเรียนตาม; ลบห้อง → ลบนักเรียนและการผูกครู

### B.4 ตัวอย่างใช้งานตั้งแต่ต้น

ทดลองผ่าน Swagger ที่ `http://127.0.0.1:8000/docs` (กด **Try it out**) หรือ curl:

```bash
BASE=http://127.0.0.1:8000/api/v1
JSON="-H Content-Type:application/json"

curl $JSON -X POST $BASE/schools    -d '{"name":"Satit","abbreviation":"SD","address":"BKK"}'
curl $JSON -X POST $BASE/classrooms -d '{"school_id":1,"year_level":1,"section":"1"}'
curl $JSON -X POST $BASE/teachers   -d '{"school_id":1,"first_name":"Somchai","last_name":"Jaidee","gender":"M","classroom_ids":[1]}'
curl $JSON -X POST $BASE/students   -d '{"classroom_id":1,"first_name":"Mana","last_name":"Dekdee","gender":"M"}'

curl "$BASE/teachers?classroom=1&lastname=jai"
curl "$BASE/schools/1"
curl "$BASE/classrooms/1"
curl $JSON -X PATCH $BASE/teachers/1 -d '{"classroom_ids":[]}'
curl -X DELETE $BASE/schools/1
```

### B.5 Status codes และรูปแบบ error

| Code | เมื่อไร | `code` |
|---|---|---|
| `201` / `200` / `204` | create / read-update / delete | |
| `404` | ไม่พบ resource ใน URL | `not_found` |
| `409` | ห้อง (ชั้นปี/ทับ) ซ้ำในโรงเรียนเดียวกัน | `conflict` |
| `422` | body/query ผิดรูปแบบ | `validation_error` (+ `errors`) |
| `422` | ผิดกฎธุรกิจ: อ้าง id ที่ไม่มี, ผูกครูข้ามโรงเรียน, ย้ายห้องที่มีครูไปโรงเรียนอื่น | `business_rule_violation` |

```json
{"detail": "Classrooms [3] do not belong to school 1", "code": "business_rule_violation"}
```

### B.6 โครงสร้าง layer (สำหรับนักพัฒนา)

```mermaid
flowchart LR
    Client --> P[Presentation<br/>routers · schemas · DI]
    P --> A[Application<br/>use cases · DTO · UnitOfWork]
    A --> D[Domain<br/>entities · rules · repository interfaces]
    I[Infrastructure<br/>SQLAlchemy · repositories · Alembic] -. implements .-> D
    I --> DB[(Database)]
```

| Layer | Path | หน้าที่ |
|---|---|---|
| Core | `src/core` | config, logging, error types |
| Domain | `src/domain` | entities, `Gender`, กฎ `Teacher.assign_classrooms`, repository ABC — ไม่รู้จัก FastAPI/SQLAlchemy |
| Application | `src/application` | use case ละ class (`CreateTeacher`, `GetSchoolDetail`, ...) ผ่าน `UnitOfWork` |
| Infrastructure | `src/infrastructure` | ORM models, `SqlAlchemy*Repository`, migrations |
| Presentation | `src/presentation` | routers, Pydantic schemas, exception handlers, DI |

**เพิ่ม feature ใหม่:** entity/rule ใน `domain` → use case ใน `application` → repository/model + migration ใน `infrastructure` → schema + router ใน `presentation` → test ใน `tests/unit` และ `tests/integration`

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| Django: `Couldn't import Django` | ยังไม่ได้ activate venv หรือยังไม่ `pip install -r requirements.txt` |
| Django: test error ใน template context | ใช้ Python 3.13+/3.14 → สร้าง venv ด้วย `py -3.12` |
| Django: `401` ทุก request | ยังไม่ได้ส่ง `-u user:pass` หรือยังไม่ login ที่ `/admin/` |
| Django: `POST`/`PATCH` error เรื่อง `APPEND_SLASH` หรือ GET ถูก redirect `301` | ลืม `/` ท้าย URL — Django version ต้องมี `/` ท้ายเสมอ |
| FastAPI: `no such table` | ยังไม่ได้ `uv run alembic upgrade head` |
| FastAPI: ได้ `307 Temporary Redirect` | ใส่ `/` ท้าย URL — FastAPI version ไม่ใช้ `/` ท้าย (curl ใช้ `-L` ถ้าจำเป็น) |
| FastAPI: ต่อ PostgreSQL ไม่ได้ | `docker compose up -d db` และใช้ URL `postgresql+asyncpg://...` |
| Port 8000 ถูกใช้ | ปิดอีกเวอร์ชันก่อน หรือ `runserver 8001` / `uvicorn ... --port 8001` |
