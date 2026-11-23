# คู่มือ fastapi-ddd-school — School API (FastAPI + DDD / Clean Architecture)

> ระบบ REST API จัดการ **โรงเรียน · ห้องเรียน · ครู · นักเรียน** แบบ Domain-Driven Design แยก 5 layer
> Stack: FastAPI · Pydantic v2 · SQLAlchemy 2 (async) · Alembic · SQLite / PostgreSQL · pytest · uv
> ตำแหน่งโปรเจกต์: `C:\github\backtend-test-2026\fastapi-ddd-school`

---

## สารบัญ

1. [บทนำ](#1-บทนำ)
2. [บทนิยาม](#2-บทนิยาม)
3. [วัตถุประสงค์](#3-วัตถุประสงค์)
4. [กลุ่มเป้าหมาย](#4-กลุ่มเป้าหมาย)
5. [ความรู้พื้นฐานที่ควรมี](#5-ความรู้พื้นฐานที่ควรมี)
6. [เนื้อหาโดยย่อ](#6-เนื้อหาโดยย่อ)
7. [โครงสร้างโฟลเดอร์](#7-โครงสร้างโฟลเดอร์--folder-structure)
8. [หลักการทำงาน (Concept)](#8-หลักการทำงาน-concept)
9. [โครงสร้างการทำงาน](#9-โครงสร้างการทำงาน)
10. [Workflow และ Dataflow](#10-workflow-และ-dataflow)
11. [การติดตั้ง](#11-การติดตั้ง)
12. [การทดสอบ + Check List Test](#12-การทดสอบ--คู่มือการทดสอบ)
13. [การใช้งาน (คู่มือการใช้งาน)](#13-การใช้งาน--คู่มือการใช้งาน)
14. [สรุป](#14-สรุป)
15. [Code Review / PR Check List](#15-ออกแบบ-code-review--code-pr)
16. [Root Cause Solution](#16-root-cause-solution)

---

## 1. บทนำ

`fastapi-ddd-school` ทำ requirement เดียวกับ `exam_app` (Django) แต่ออกแบบให้ **กฎธุรกิจไม่ผูกกับ framework**
โค้ดแบ่งเป็น Core / Domain / Application / Infrastructure / Presentation โดย Domain อยู่ตรงกลางและไม่ import FastAPI, SQLAlchemy หรือ Pydantic
ผลคือ test กฎธุรกิจได้โดยไม่ต้องมี DB และเปลี่ยน DB (SQLite ↔ PostgreSQL) ได้โดยไม่ต้องแก้ use case

```mermaid
erDiagram
    SCHOOLS ||--o{ CLASSROOMS : "ON DELETE CASCADE"
    SCHOOLS ||--o{ TEACHERS : "ON DELETE CASCADE"
    CLASSROOMS ||--o{ STUDENTS : "ON DELETE CASCADE"
    TEACHERS ||--o{ TEACHER_CLASSROOMS : ""
    CLASSROOMS ||--o{ TEACHER_CLASSROOMS : ""
    CLASSROOMS { int id int school_id int year_level string section "UNIQUE(school_id, year_level, section)" }
    TEACHERS { int id int school_id string first_name string last_name char gender "CHECK M/F/O" }
```

## 2. บทนิยาม

| คำ | ความหมาย | ในโปรเจกต์ |
|---|---|---|
| **DDD** (Domain-Driven Design) | ออกแบบซอฟต์แวร์โดยยึดกฎธุรกิจเป็นศูนย์กลาง | `src/domain` |
| **Clean / Onion Architecture** | dependency ชี้เข้าหาแกนกลางเท่านั้น | Presentation → Application → Domain ← Infrastructure |
| **Entity** | object ที่มี id และตรวจความถูกต้องของตัวเอง | `Teacher`, `Classroom` (dataclass) |
| **Value Object** | ค่าที่ไม่มี id, เทียบกันด้วยค่า | `Gender`, `non_blank()` |
| **Repository (interface)** | สัญญาการอ่าน/เขียนข้อมูล ไม่ระบุเทคโนโลยี | `TeacherRepository(ABC)` |
| **Repository (implementation)** | การทำงานจริงด้วย SQLAlchemy | `SqlAlchemyTeacherRepository` |
| **Use Case** | 1 class = 1 งานทางธุรกิจ | `CreateTeacher`, `GetSchoolDetail` |
| **Unit of Work (UoW)** | รวม repository ของ 1 transaction และ commit/rollback ครั้งเดียว | `SqlAlchemyUnitOfWork` |
| **DTO** | ข้อมูลที่ส่งระหว่าง layer | `TeacherInput`, `SchoolDetail`, `Page` |
| **Schema** | Pydantic model ของ HTTP request/response | `TeacherIn`, `TeacherPatch`, `TeacherOut` |
| **Composition Root** | จุดเดียวที่ผูก interface กับ implementation | `presentation/dependencies/database.py` |
| **Criteria** | เงื่อนไขค้นหาที่ส่งเข้า repository | `PersonCriteria` |
| **selectin loading** | โหลด relationship ด้วย `SELECT ... WHERE id IN (...)` 1 ครั้งต่อหน้า | `TeacherModel.classrooms` |

## 3. วัตถุประสงค์

1. API CRUD ครบ 4 resource พร้อม filter, pagination, detail
2. แยกกฎธุรกิจออกจาก framework เพื่อให้ทดสอบง่ายและเปลี่ยนเทคโนโลยีได้
3. Error format เดียวกันทั้งระบบ: `{"detail", "code"}` แยกประเภท 404 / 409 / 422
4. รองรับ SQLite (dev) และ PostgreSQL (prod) ด้วย config เดียว
5. จำนวน query คงที่ทุก endpoint (ไม่มี N+1) และใช้ async I/O

## 4. กลุ่มเป้าหมาย

- Backend developer ที่ต้องการเรียนรู้/ดูแลโปรเจกต์ DDD + FastAPI
- Tech lead / Architect ที่ต้องการตัวอย่างการแยก layer
- Frontend / Mobile developer ที่เรียก API (ดู `/docs`)
- QA ที่ทดสอบ API ด้วย Postman / pytest

## 5. ความรู้พื้นฐานที่ควรมี

- Python 3.11+ (`dataclass`, `StrEnum`, type hints, `async/await`)
- FastAPI: router, `Depends`, `response_model`
- Pydantic v2: `BaseModel`, `Field`, `model_dump(exclude_unset=True)`
- SQLAlchemy 2.0: `select()`, `AsyncSession`, relationship
- Alembic migration, pytest + pytest-asyncio
- แนวคิด SOLID โดยเฉพาะ Dependency Inversion

## 6. เนื้อหาโดยย่อ

| หัวข้อ | สาระสำคัญ | ประโยชน์ |
|---|---|---|
| 5 layer | Domain ไม่รู้จัก framework | แก้ DB/HTTP ไม่กระทบกฎธุรกิจ |
| Entity ตรวจตัวเอง | `__post_init__` ตรวจ blank/length/gender | สร้าง object ผิดไม่ได้ตั้งแต่ต้น |
| `Teacher.assign_classrooms` | กฎ "ครูสอนห้องโรงเรียนตัวเองเท่านั้น" อยู่ใน entity | กฎอยู่ที่เดียว ใช้ทั้ง create/update |
| Use case + UoW | 1 use case = 1 transaction | commit ครั้งเดียว, ผิดพลาด rollback อัตโนมัติ |
| Exception mapping | `NotFoundError→404`, `ConflictError→409`, `BusinessRuleError→422` | domain ไม่ต้องรู้ HTTP status |
| Test pyramid | unit (mock repo) + integration (HTTP + SQLite in-memory) | 70 tests รันใน ~7 วินาที |

## 7. โครงสร้างโฟลเดอร์ | folder-structure

```text
fastapi-ddd-school/
├── src/
│   ├── main.py                        # create_app(): ลง router, exception handler, /health
│   ├── core/                          # ใช้ได้ทุก layer
│   │   ├── config.py                  # Settings (pydantic-settings, อ่าน .env)
│   │   ├── exceptions.py              # AppError, NotFoundError, ConflictError, BusinessRuleError
│   │   └── logging.py
│   ├── domain/                        # ❌ ไม่ import FastAPI / SQLAlchemy / Pydantic
│   │   ├── entities/                  # school.py, classroom.py, teacher.py, student.py
│   │   ├── value_objects/             # gender.py (StrEnum), text.py (non_blank)
│   │   ├── repositories/              # *_repository.py (ABC), criteria.py (PersonCriteria)
│   │   └── services/
│   ├── application/                   # ❌ ไม่ import FastAPI / SQLAlchemy
│   │   ├── unit_of_work.py            # UnitOfWork (ABC)
│   │   ├── dto/                       # inputs.py, details.py, pagination.py
│   │   └── use_cases/
│   │       ├── base.py                # UseCase, get_or_404, ensure_reference
│   │       └── {school,classroom,teacher,student}/{commands,queries}.py
│   ├── infrastructure/                # ❌ ไม่ import FastAPI
│   │   ├── db/                        # base.py (DeclarativeBase), session.py (engine, SQLite FK pragma)
│   │   ├── models/                    # SchoolModel, ClassroomModel, TeacherModel, StudentModel, teacher_classrooms
│   │   ├── repositories/              # SqlAlchemy*Repository, base.py (_flush, _paginate), unit_of_work.py
│   │   └── migrations/                # Alembic env.py + versions/0001_initial_schema.py
│   └── presentation/
│       ├── api/v1/                    # schools.py, classrooms.py, teachers.py, students.py
│       ├── schemas/                   # Pydantic In / Patch / Out / DetailOut
│       ├── dependencies/              # database.py (composition root), pagination.py
│       └── exception_handlers.py      # AppError → HTTP status
├── tests/
│   ├── conftest.py                    # SQLite in-memory + override get_session
│   ├── unit/                          # test_entities.py, test_use_cases.py (AsyncMock)
│   └── integration/                   # test_{schools,classrooms,teachers,students}.py
├── .env.example · alembic.ini · pyproject.toml · uv.lock
├── Dockerfile · docker-compose.yml    # api + postgres:16
└── README.md
```

## 8. หลักการทำงาน (Concept)

### 8.1 Dependency Rule

```mermaid
flowchart LR
    P[Presentation<br/>routers · schemas · DI] --> A[Application<br/>use cases · DTO · UoW ABC]
    A --> D[Domain<br/>entities · value objects · repo ABC]
    I[Infrastructure<br/>SQLAlchemy · Alembic] -. implements .-> D
    I -. implements UoW .-> A
    CR[Composition root<br/>dependencies/database.py] --> I
    P --> CR
    D --> C[Core<br/>exceptions · config]
```

- ลูกศรทึบ = import ได้, ลูกศรประ = implement interface
- **Domain** ไม่ import อะไรนอกจาก `core` → เป็นแกนที่เสถียรที่สุด
- **Infrastructure** เป็นฝ่าย implement interface ของ Domain (Dependency Inversion)
- **Router** รับ `UnitOfWork` (abstract) ผ่าน `Depends(get_uow)` จึงไม่รู้ว่าเบื้องหลังเป็น SQLAlchemy

### 8.2 แบ่งการตรวจสอบ 3 ชั้น

| ชั้น | ใครตรวจ | ตัวอย่าง | Status |
|---|---|---|---|
| รูปแบบ request | Pydantic schema | `school_id` ต้องเป็น int > 0, `page_size ≤ 100`, PATCH ส่ง `null` | 422 `validation_error` |
| กฎของ entity | Entity / Value Object | ชื่อว่าง, gender ไม่ใช่ M/F/O, ครูผูกห้องต่างโรงเรียน | 422 `business_rule_violation` |
| กฎที่ต้องดู DB | Use case + repository | id ที่อ้างไม่มีอยู่ (422), ห้องซ้ำ (409), resource ใน URL ไม่มี (404) | 404 / 409 / 422 |

### 8.3 404 กับ 422 ต่างกันอย่างไร
- `get_or_404` — id ใน **URL** ไม่มี → 404 (`/teachers/99`)
- `ensure_reference` — id ใน **body** ไม่มี → 422 (`{"school_id": 99}`) เพราะ URL ถูกต้อง แต่ข้อมูลที่ส่งผิดกฎ

## 9. โครงสร้างการทำงาน

| Layer | ไฟล์หลัก | Input | Output | ไม่รู้จัก |
|---|---|---|---|---|
| Presentation | `api/v1/teachers.py` | HTTP + JSON | `TeacherOut` JSON | SQLAlchemy |
| Application | `use_cases/teacher/commands.py` | `TeacherInput` DTO | `Teacher` entity | FastAPI, SQLAlchemy |
| Domain | `entities/teacher.py` | ค่า primitive | entity ที่ถูกต้อง หรือ `BusinessRuleError` | ทุก framework |
| Infrastructure | `repositories/teacher_repository.py` | entity | entity (มี id) | FastAPI |
| DB | SQLite / PostgreSQL | SQL | rows | — |

## 10. Workflow และ Dataflow

### 10.1 Workflow ภาพรวมของ 1 request

```mermaid
flowchart TD
    A([HTTP Request]) --> B[FastAPI Router<br/>/api/v1/...]
    B --> C{Pydantic schema<br/>ตรวจ body / query / path}
    C -- ไม่ผ่าน --> E422v[422 validation_error<br/>+ errors]
    C -- ผ่าน --> D[Depends: get_session → get_uow<br/>เปิด AsyncSession + SqlAlchemyUnitOfWork]
    D --> U[Use case.execute&#40;DTO&#41;]
    U --> G{resource ใน URL มี?<br/>get_or_404}
    G -- ไม่มี --> E404[NotFoundError → 404 not_found]
    G -- มี / เป็น create --> R{id ที่อ้างใน body มี?<br/>ensure_reference}
    R -- ไม่มี --> E422b[BusinessRuleError → 422]
    R -- มี --> EN{Entity ตรวจกฎ<br/>__post_init__ / assign_classrooms}
    EN -- ผิดกฎ --> E422b
    EN -- ผ่าน --> UQ{ข้อมูลซ้ำ?<br/>exists_duplicate}
    UQ -- ซ้ำ --> E409[ConflictError → 409 conflict]
    UQ -- ไม่ซ้ำ --> S[repository.save → flush]
    S --> CM[uow.commit]
    CM -- IntegrityError<br/>(race condition) --> E409
    CM -- สำเร็จ --> RESP[response_model แปลง entity → JSON<br/>201 / 200 / 204]
    E404 & E422b & E409 --> H[exception_handlers.py<br/>JSON detail + code]
    D -. ออกจาก context .-> CL[ปิด session<br/>ที่ยังไม่ commit = rollback]
```

**คำอธิบายละเอียด**

1. **Router** — `main.py` รวม router 4 ตัวใต้ prefix `/api/v1` แต่ละ router ระบุ `response_model` และ `ERROR_RESPONSES` (ขึ้นใน OpenAPI `/docs`)
2. **Schema validation** — FastAPI แปลง JSON เป็น `TeacherIn` / `TeacherPatch` ถ้าไม่ผ่าน `validation_error_handler` คืน 422 พร้อม `errors` ของ Pydantic
3. **Dependency Injection** — `get_session()` เปิด `AsyncSession` 1 ตัวต่อ request แล้ว `get_uow()` ห่อเป็น `SqlAlchemyUnitOfWork` ที่มี repository ครบ 4 ตัวบน session เดียวกัน (= transaction เดียว)
4. **Use case** — router แปลง schema เป็น DTO (`TeacherInput(**body.model_dump())`) แล้วเรียก `CreateTeacher(uow).execute(...)` use case เป็นที่เดียวที่ลำดับขั้นตอนทางธุรกิจ
5. **Entity** — สร้าง `Teacher(...)` จะตรวจตัวเองทันที (`non_blank`, `Gender.parse`) และ `assign_classrooms()` ตรวจกฎข้ามโรงเรียน
6. **Persist** — `repository.save()` แปลง entity → ORM model แล้ว `flush()` (ได้ id) ยังไม่ commit
7. **Commit** — `uow.commit()` ถ้าชน constraint (เช่น 2 request สร้างห้องซ้ำพร้อมกัน) แปลง `IntegrityError` เป็น `ConflictError` → 409
8. **Response** — `OutModel` (`from_attributes=True`) อ่าน attribute ของ entity/DTO เป็น JSON
9. **Error** — ทุก `AppError` ไปที่ `app_error_handler` ซึ่ง map class → status ตาม `_STATUS_BY_ERROR`
10. **Cleanup** — ออกจาก `async with SessionFactory()` session ถูกปิด อะไรที่ไม่ commit จะ rollback อัตโนมัติ

### 10.2 Dataflow: POST /api/v1/teachers (แปลงข้อมูลผ่านทุก layer)

```mermaid
flowchart TD
    J[/"JSON<br/>{school_id:1, first_name:' Somchai ',<br/>last_name:'Jaidee', gender:'M', classroom_ids:[1,1,2]}"/]
    J -->|Pydantic| TI["TeacherIn<br/>first_name='Somchai' (strip)<br/>gender=Gender.MALE"]
    TI -->|model_dump| DTO["TeacherInput (frozen dataclass)"]
    DTO -->|CreateTeacher.execute| E1["Teacher entity<br/>__post_init__ ✔"]
    E1 --> R1[(SELECT school 1<br/>ensure_reference)]
    R1 --> R2[(SELECT classrooms WHERE id IN 1,2<br/>get_many)]
    R2 --> M{missing ids?}
    M -- มี --> X1[422 Classrooms 2 do not exist]
    M -- ไม่มี --> AC{"assign_classrooms<br/>ทุกห้อง school_id == 1 ?"}
    AC -- ไม่ --> X2[422 Classrooms 2 do not belong to school 1]
    AC -- ใช่ --> E2["Teacher.classroom_ids = [1,2]<br/>(ตัดซ้ำ + เรียง)"]
    E2 -->|SqlAlchemyTeacherRepository.save| ORM["TeacherModel + classrooms"]
    ORM --> F[(INSERT teachers<br/>INSERT teacher_classrooms ×2<br/>flush)]
    F --> C[(COMMIT)]
    C -->|_to_entity| E3["Teacher id=1"]
    E3 -->|TeacherOut| OUT[/"201 {id:1, school_id:1, first_name:'Somchai',<br/>last_name:'Jaidee', gender:'M', classroom_ids:[1,2]}"/]
```

### 10.3 Dataflow: PATCH /api/v1/teachers/{id} (เปลี่ยนโรงเรียน)

```mermaid
flowchart TD
    P[/"PATCH {school_id: 2}"/] --> TP["TeacherPatch<br/>ส่ง null? → 422"]
    TP -->|changes&#40;&#41; = exclude_unset| CH["{school_id: 2}"]
    CH --> G[get_or_404 teacher → current]
    G --> RP["replace(current, school_id=2)<br/>classroom_ids เดิม [1]"]
    RP --> ER[ensure_reference school 2]
    ER --> AS{"ห้อง 1 อยู่โรงเรียน 2?"}
    AS -- ไม่ --> X[422: ต้องส่ง classroom_ids ใหม่มาด้วย]
    AS -- ใช่ --> SV[save + commit → 200]
```

> ใช้ `dataclasses.replace()` จึงสร้าง entity ใหม่และ `__post_init__` ทำงานซ้ำ → ค่าที่ PATCH มาถูกตรวจกฎเหมือนตอน create

### 10.4 Dataflow: GET /api/v1/schools/{id} — 1 query ได้ 3 count

```mermaid
flowchart LR
    R[GET /schools/1] --> Q1[(SELECT school WHERE id=1)]
    Q1 --> Q2[("SELECT<br/>(SELECT count FROM classrooms WHERE school_id=1),<br/>(SELECT count FROM teachers WHERE school_id=1),<br/>(SELECT count FROM students JOIN classrooms ...)")]
    Q2 --> D[SchoolDetail DTO] --> O[/"200 {..., classroom_count,<br/>teacher_count, student_count}"/]
```

ใช้ scalar subquery 3 ตัวแทนการ JOIN classroom × teacher × student (ซึ่งจะทำให้แถวคูณกันและ count ผิด)

### 10.5 Dataflow: GET list + filter + pagination

```mermaid
flowchart LR
    Q[/"GET /teachers?classroom=1&firstname=som&page=1&page_size=20"/] --> PC[PersonCriteria]
    PC --> ST["select(TeacherModel)<br/>+ WHERE EXISTS teacher_classrooms<br/>+ first_name ILIKE '%som%' (autoescape)"]
    ST --> CNT[(SELECT count&#40;*&#41; FROM &#40;subquery&#41;)]
    ST --> PG[(LIMIT 20 OFFSET 0)]
    PG --> SEL[(selectin: classrooms<br/>WHERE teacher_id IN ...)]
    CNT & SEL --> OUT[/"{items, total, page, page_size}"/]
```

## 11. การติดตั้ง

**ต้องมี:** Python 3.11+, [uv](https://docs.astral.sh/uv/), (ถ้าใช้ PostgreSQL) Docker Desktop

### 11.1 แบบ SQLite (แนะนำสำหรับ dev)

```powershell
cd C:\github\backtend-test-2026\fastapi-ddd-school

uv sync                                  # สร้าง .venv + ติดตั้ง dependency (รวม dev)
Copy-Item .env.example .env              # Git Bash: cp .env.example .env
uv run alembic upgrade head              # สร้างตาราง school.db
uv run uvicorn src.main:app --reload     # http://127.0.0.1:8000/docs
```

ตรวจว่าสำเร็จ: `curl http://127.0.0.1:8000/health` → `{"status":"ok"}`

### 11.2 แบบ PostgreSQL

```powershell
docker compose up -d db
# แก้ .env:
# DATABASE_URL=postgresql+asyncpg://school:school@localhost:5432/school
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

### 11.3 แบบ Docker ทั้งระบบ

```powershell
docker compose up --build     # API :8000 รัน alembic upgrade head ให้อัตโนมัติก่อน start
```

### 11.4 ตัวแปร environment

| Env | Default | คำอธิบาย |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./school.db` | ต้องเป็น async driver (`sqlite+aiosqlite` / `postgresql+asyncpg`) |
| `SQL_ECHO` | `false` | `true` = log SQL ทุกคำสั่ง (ใช้ debug N+1) |
| `LOG_LEVEL` | `INFO` | |

### 11.5 สร้าง migration หลังแก้ model

```powershell
uv run alembic revision --autogenerate -m "add teacher email"
uv run alembic upgrade head
```

## 12. การทดสอบ | คู่มือการทดสอบ

### 12.1 รัน test

```powershell
uv run pytest                         # ทั้งหมด
uv run pytest tests/unit -q           # เฉพาะ unit (ไม่ใช้ DB)
uv run pytest tests/integration/test_teachers.py -v
uv run pytest -k "gender"             # เลือกตามชื่อ
```

ผลที่ได้จริง (รันเมื่อ 2026-11-23):

```text
70 passed in 7.20s
```

### 12.2 Test pyramid

```mermaid
flowchart TB
    subgraph I["Integration (tests/integration) — HTTP จริงผ่าน httpx.ASGITransport + SQLite in-memory"]
      I1[schools 12] --- I2[classrooms 11] --- I3[teachers 17] --- I4[students 13]
    end
    subgraph U["Unit (tests/unit) — ไม่มี DB"]
      U1[test_entities: กฎ entity] --- U2[test_use_cases: AsyncMock repository]
    end
    U --> I
```

- **Unit**: mock repository ด้วย `AsyncMock(spec=TeacherRepository)` แล้วตรวจว่าเมื่อผิดกฎ `save` และ `commit` **ไม่ถูกเรียก**
- **Integration**: `tests/conftest.py` สร้าง engine ใหม่ทุก test (`StaticPool` + in-memory) และ `app.dependency_overrides[get_session]` → test แยกกันสมบูรณ์

### 12.3 ตัวอย่าง unit test ที่รันได้จริง

```python
# tests/unit/test_my_rule.py
import pytest
from src.core.exceptions import BusinessRuleError
from src.domain.entities.classroom import Classroom
from src.domain.entities.teacher import Teacher


def test_teacher_cannot_teach_other_school():
    teacher = Teacher(school_id=1, first_name="A", last_name="B", gender="M")
    with pytest.raises(BusinessRuleError):
        teacher.assign_classrooms([Classroom(id=9, school_id=2, year_level=1, section="1")])


def test_classroom_ids_are_deduplicated_and_sorted():
    teacher = Teacher(school_id=1, first_name="A", last_name="B", gender="M")
    rooms = [Classroom(id=i, school_id=1, year_level=1, section=str(i)) for i in (3, 1, 3)]
    teacher.assign_classrooms(rooms)
    assert teacher.classroom_ids == [1, 3]
```

```powershell
uv run pytest tests/unit/test_my_rule.py -q
```

### 12.4 Check List Test

**CRUD**
- [ ] POST ทุก resource → 201 และมี `id`
- [ ] GET list → `{items, total, page, page_size}`
- [ ] GET `/{id}` ไม่มี → 404 `not_found`
- [ ] PUT ส่งไม่ครบ field → 422 `validation_error`
- [ ] PATCH ส่งบาง field → 200, field อื่นไม่เปลี่ยน
- [ ] PATCH ส่ง `null` → 422
- [ ] DELETE → 204, GET ซ้ำ → 404

**Filter / Pagination**
- [ ] `schools?name=` contains, ไม่สนตัวพิมพ์
- [ ] `name=%` หรือ `name=_` ไม่ match ทุกแถว (autoescape)
- [ ] `classrooms?school=`
- [ ] `teachers` / `students` filter `school`, `classroom`, `firstname`, `lastname`, `gender`
- [ ] `gender=X` → 422
- [ ] `page=0` → 422, `page_size=101` → 422, `page` เกินข้อมูล → `items: []`

**Business rule**
- [ ] ห้องซ้ำ (school, year_level, section) → 409 `conflict`
- [ ] อ้าง `school_id` / `classroom_id` / `classroom_ids` ที่ไม่มี → 422 `business_rule_violation`
- [ ] ครูผูกห้องต่างโรงเรียน → 422
- [ ] PATCH ครูเปลี่ยน school โดยไม่ส่งห้องใหม่ (ห้องเดิมอยู่โรงเรียนเก่า) → 422
- [ ] PATCH ครูเปลี่ยน school + `classroom_ids` ของโรงเรียนใหม่ → 200
- [ ] ย้ายห้องไปโรงเรียนอื่นขณะมีครูโรงเรียนเดิม → 422
- [ ] ชื่อเป็นช่องว่างล้วน → 422; `year_level < 1` → 422

**Detail / Performance**
- [ ] School detail count ถูกทั้ง 3 ค่า
- [ ] Classroom detail มี `teachers`, `students`
- [ ] Teacher detail มี `classrooms` (object), Student detail มี `classroom`
- [ ] ตั้ง `SQL_ECHO=true` แล้วจำนวน query ไม่เพิ่มตามจำนวนแถว

**Cascade**
- [ ] ลบ school → classroom/teacher/student ของโรงเรียนนั้นหาย (ทั้ง SQLite และ PostgreSQL)
- [ ] ลบ classroom → student ในห้องหาย, ครูอยู่แต่ไม่มีห้องนั้นใน `classroom_ids`

**Non-functional**
- [ ] `/health` → 200
- [ ] `/docs` เปิดได้ และแสดง error response 404/409/422
- [ ] `alembic upgrade head` บน DB ว่างสำเร็จ

## 13. การใช้งาน | คู่มือการใช้งาน

### 13.1 Endpoint

Base URL: `http://127.0.0.1:8000/api/v1` (ไม่มี `/` ท้าย) · Swagger UI: `/docs` · ReDoc: `/redoc`

| Resource | List / Create | Get / PUT / PATCH / DELETE | Query filter | Detail เพิ่ม |
|---|---|---|---|---|
| School | `/schools` | `/schools/{id}` | `name` | `classroom_count`, `teacher_count`, `student_count` |
| Classroom | `/classrooms` | `/classrooms/{id}` | `school` | `teachers`, `students` |
| Teacher | `/teachers` | `/teachers/{id}` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classrooms` |
| Student | `/students` | `/students/{id}` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classroom` |

ทุก list รับ `page` (default 1) และ `page_size` (default 20, สูงสุด 100)

### 13.2 ตัวอย่าง curl ที่รันได้จริง (Git Bash)

```bash
BASE=http://127.0.0.1:8000/api/v1
H='Content-Type: application/json'

curl -s -X POST $BASE/schools    -H "$H" -d '{"name":"Satit","abbreviation":"SD","address":"BKK"}'
curl -s -X POST $BASE/classrooms -H "$H" -d '{"school_id":1,"year_level":1,"section":"1"}'
curl -s -X POST $BASE/teachers   -H "$H" -d '{"school_id":1,"first_name":"Somchai","last_name":"Jaidee","gender":"M","classroom_ids":[1]}'
curl -s -X POST $BASE/students   -H "$H" -d '{"classroom_id":1,"first_name":"Mana","last_name":"Dekdee","gender":"M"}'

curl -s $BASE/schools/1
# {"id":1,"name":"Satit","abbreviation":"SD","address":"BKK","classroom_count":1,"teacher_count":1,"student_count":1}

curl -s "$BASE/teachers?classroom=1&firstname=som&page_size=10"
# {"items":[{...}],"total":1,"page":1,"page_size":10}

curl -s -X PATCH $BASE/teachers/1 -H "$H" -d '{"last_name":"Jaidee-Dee"}'
curl -s -X DELETE $BASE/schools/1 -o /dev/null -w "%{http_code}\n"     # 204
```

### 13.3 ตัวอย่าง Python client (async)

```python
import asyncio
import httpx

async def main() -> None:
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1") as c:
        school = (await c.post("/schools", json={"name": "A", "abbreviation": "A", "address": "x"})).json()
        room = (await c.post("/classrooms", json={"school_id": school["id"], "year_level": 1, "section": "1"})).json()
        r = await c.post("/teachers", json={
            "school_id": school["id"], "first_name": "T", "last_name": "L",
            "gender": "M", "classroom_ids": [room["id"]],
        })
        print(r.status_code, r.json())

asyncio.run(main())
```

### 13.4 รูปแบบ Error

| Status | เมื่อไร | `code` |
|---|---|---|
| 404 | ไม่พบ resource ใน URL | `not_found` |
| 409 | ห้อง (ชั้นปี/ทับ) ซ้ำในโรงเรียนเดียวกัน | `conflict` |
| 422 | body/query ผิดรูปแบบ | `validation_error` (+ `errors`) |
| 422 | ผิดกฎธุรกิจ | `business_rule_violation` |

```json
{"detail": "Classrooms [3] do not belong to school 1", "code": "business_rule_violation"}
```

### 13.5 ทดสอบด้วย Postman CLI

Import OpenAPI จาก `http://127.0.0.1:8000/openapi.json` เข้า Postman เพื่อสร้าง collection อัตโนมัติ แล้วรัน:

```powershell
postman collection run <collection-id-หรือ-ไฟล์.json> --env-var "baseUrl=http://127.0.0.1:8000"
```

### 13.6 การเพิ่ม resource / feature ใหม่ (ลำดับไฟล์)

```mermaid
flowchart LR
    A[1 domain/entities<br/>+ กฎใน entity] --> B[2 domain/repositories<br/>ABC]
    B --> C[3 application/dto<br/>+ use_cases]
    C --> D[4 infrastructure/models<br/>+ repository + UoW]
    D --> E[5 alembic revision]
    E --> F[6 presentation/schemas<br/>+ api/v1 router]
    F --> G[7 main.py include_router]
    G --> H[8 tests unit + integration]
```

## 14. สรุป

### ประโยชน์ที่ได้รับ
- กฎธุรกิจอยู่ที่เดียว (entity/use case) ทุกทางเข้าต้องผ่าน
- test กฎธุรกิจได้เร็วโดยไม่ใช้ DB; integration test ครอบ HTTP จริง (รวม 70 tests)
- error มี `code` ให้ frontend แยกจัดการได้
- เปลี่ยน SQLite ↔ PostgreSQL ด้วย env ตัวเดียว
- OpenAPI `/docs` สร้างอัตโนมัติพร้อม error response

### ข้อดี
- แยก layer ชัด ทีมใหญ่ทำงานคู่ขนานได้ (คนทำ domain / คนทำ API)
- async I/O รองรับ concurrent สูง
- query คงที่ (scalar subquery, selectin, EXISTS)
- race condition ห้องซ้ำถูกจับโดย DB constraint → 409

### ข้อเสีย
- ไฟล์และ boilerplate เยอะกว่า Django ประมาณ 3–4 เท่า (entity + model + schema + DTO + mapper)
- ต้องแปลงข้อมูลหลายรอบ (schema → DTO → entity → ORM model → entity → schema)
- ไม่มี Admin UI สำเร็จรูป
- ต้องเข้าใจ async SQLAlchemy (lazy load ใช้ไม่ได้)

### ข้อควรระวัง
- **ห้าม lazy load ใน async** — relationship ต้องเป็น `selectin` หรือโหลดก่อน (ดู comment ใน `SqlAlchemyTeacherRepository.save`)
- SQLite จะไม่ทำ `ON DELETE CASCADE` ถ้าไม่เปิด `PRAGMA foreign_keys=ON` (ทำแล้วใน `build_engine`) — ถ้าสร้าง engine เองต้องใช้ `build_engine`
- `get_settings()` ถูก `lru_cache` — เปลี่ยน env ระหว่างรันต้อง restart
- `.env` ถูก ignore ใน git แล้ว อย่าเอา credential จริงใส่ `.env.example`
- ยังไม่มี authentication/authorization

### ข้อห้าม
- ห้าม import `fastapi`, `sqlalchemy`, `pydantic` ใน `src/domain` และห้าม import `fastapi`/`sqlalchemy` ใน `src/application`
- ห้ามเรียก `session.commit()` ใน repository — commit ผ่าน `uow.commit()` ใน use case เท่านั้น
- ห้าม router เรียก repository ตรง ต้องผ่าน use case
- ห้ามคืน ORM model ออกจาก repository ต้องแปลงเป็น entity (`_to_entity`)
- ห้ามแก้ migration ที่ apply แล้ว

## 15. ออกแบบ Code Review / Code PR

### 15.1 ขั้นตอน PR

```mermaid
flowchart LR
    A[branch feature/xxx] --> B[เขียน test ก่อน<br/>unit + integration]
    B --> C[implement ตาม layer]
    C --> D[uv run pytest]
    D --> E[alembic revision ถ้าแก้ model]
    E --> F[เปิด PR]
    F --> G{Review checklist}
    G -- แก้ --> C
    G -- Approve --> H[Merge main]
```

### 15.2 PR Template

```markdown
## สรุปการเปลี่ยนแปลง
-
## Layer ที่แก้
- [ ] domain  - [ ] application  - [ ] infrastructure  - [ ] presentation  - [ ] migration
## วิธีทดสอบ
- [ ] uv run pytest ผ่าน (__ tests)
- [ ] ทดสอบผ่าน /docs หรือ curl: ...
## Breaking change ของ API
- [ ] ไม่มี / มี (อธิบาย)
```

### 15.3 Code Review Check List

**Architecture**
- [ ] dependency ชี้เข้าใน (`grep -rn "sqlalchemy\|fastapi\|pydantic" src/domain` ต้องว่าง)
- [ ] กฎธุรกิจอยู่ใน entity หรือ use case ไม่อยู่ใน router/schema/repository
- [ ] use case 1 class = 1 งาน และ commit ครั้งเดียวท้ายสุด
- [ ] router บาง: แปลง schema → DTO → เรียก use case เท่านั้น

**Domain / Application**
- [ ] entity ตรวจตัวเองใน `__post_init__`
- [ ] error ใช้ `NotFoundError` / `ConflictError` / `BusinessRuleError` ถูกประเภท (URL id → 404, body id → 422)
- [ ] update ใช้ `dataclasses.replace` เพื่อให้ validation ทำงานซ้ำ

**Infrastructure**
- [ ] repository คืน entity ไม่คืน ORM model
- [ ] ไม่มี lazy load; relationship ที่ต้องใช้กำหนด `lazy="selectin"` หรือ query เอง
- [ ] ค้นหาข้อความใช้ `icontains(..., autoescape=True)`
- [ ] list มี `order_by` และนับ total ด้วย subquery
- [ ] constraint สำคัญมีที่ DB (UNIQUE, CHECK, FK ondelete) + migration

**Presentation**
- [ ] มี `response_model` และ `status_code` ถูกต้อง
- [ ] PATCH schema สืบทอด `PatchModel`
- [ ] query param มี bound (`ge`, `le`)

**Test**
- [ ] use case ใหม่มี unit test ที่ mock repo และตรวจว่า `commit` ไม่ถูกเรียกเมื่อ error
- [ ] endpoint ใหม่มี integration test ทั้ง happy และ error path
- [ ] `uv run pytest` ผ่านทั้งหมด

## 16. Root Cause Solution

| # | อาการ | สาเหตุ (Root Cause) | วิธีแก้ |
|---|---|---|---|
| 1 | `no such table: schools` | ยังไม่รัน migration | `uv run alembic upgrade head` |
| 2 | `ModuleNotFoundError: No module named 'src'` | รันจากโฟลเดอร์ผิด หรือรัน `python src/main.py` ตรง | รันที่ root โปรเจกต์ด้วย `uv run uvicorn src.main:app` |
| 3 | `The asyncio extension requires an async driver` | `DATABASE_URL` ใช้ `sqlite://` หรือ `postgresql://` | ใช้ `sqlite+aiosqlite://` / `postgresql+asyncpg://` |
| 4 | `MissingGreenlet: greenlet_spawn has not been called` | lazy load relationship ใน async | ใช้ `lazy="selectin"`, `selectinload()` หรือ query ก่อนแก้ model |
| 5 | ลบ school แล้ว classroom ยังอยู่ (SQLite) | ไม่ได้เปิด `PRAGMA foreign_keys=ON` | สร้าง engine ด้วย `build_engine()` เสมอ |
| 6 | 409 `The data conflicts with an existing record` | ชน UNIQUE constraint (มักเกิดจาก 2 request พร้อมกัน) | ถูกต้องตามออกแบบ; client retry หรือแจ้งผู้ใช้ |
| 7 | 422 `Classrooms [x] do not belong to school y` | PATCH `school_id` โดยห้องเดิมยังอยู่โรงเรียนเก่า | ส่ง `school_id` พร้อม `classroom_ids` ใหม่ (หรือ `[]`) ใน request เดียว |
| 8 | 422 `Fields cannot be null` | PATCH ส่ง `null` | ไม่ต้องส่ง field ที่ไม่แก้ |
| 9 | 404 แต่ URL ถูก | ใส่ `/` ท้าย (`/schools/`) ทำให้ redirect 307 หรือ id ไม่มี | ใช้ `/api/v1/schools` ไม่มี `/` ท้าย |
| 10 | `Connection refused` port 5432 | Postgres ยังไม่ขึ้น | `docker compose up -d db` แล้วรอ healthcheck (`docker compose ps`) |
| 11 | test ผ่านทีละไฟล์แต่รวมแล้ว fail | test ใช้ state ร่วมกัน / ไม่ใช้ fixture `client` | ใช้ fixture `client` + `session_factory` ที่สร้าง DB ใหม่ทุก test |
| 12 | `ScopeMismatch` / event loop closed ใน pytest | fixture async ต่าง scope | ใช้ `asyncio_mode = "auto"` และ loop scope `function` (ตั้งไว้ใน `pyproject.toml`) |
| 13 | ค่าใน `.env` ไม่ถูกใช้ | `get_settings()` cache ไว้ หรือรันคนละโฟลเดอร์กับ `.env` | restart server และรันที่ root โปรเจกต์ |
| 14 | Response ช้าเมื่อข้อมูลเยอะ | N+1 หรือ JOIN คูณแถว | ตั้ง `SQL_ECHO=true` ดู SQL; ใช้ selectin / EXISTS / scalar subquery |

**ขั้นตอนหาสาเหตุ**

```mermaid
flowchart TD
    A[พบปัญหา] --> B[ทำซ้ำด้วย curl หรือเขียน integration test]
    B --> C{status / code}
    C -- 422 validation_error --> D[ดู errors → แก้ schema หรือ request]
    C -- 422 business_rule_violation --> E[ดู entity / use case ที่ raise]
    C -- 404 / 409 --> F[ดู get_or_404 / exists_duplicate / constraint]
    C -- 500 --> G[อ่าน traceback ใน log uvicorn<br/>เปิด SQL_ECHO=true]
    D & E & F & G --> H[เขียน test ที่ fail ใน layer ที่ต่ำที่สุดที่ทำซ้ำได้<br/>unit ก่อน integration]
    H --> I[แก้โค้ด → uv run pytest ผ่านทั้งหมด]
```
