# School API — FastAPI + DDD

ระบบจัดการโรงเรียน ห้องเรียน ครู และนักเรียน (requirement เดียวกับ `4_rest_api/api_exam.md`)
ออกแบบตามแนวทาง [fastapi-ddd-template](https://github.com/CodesForge/fastapi-ddd-template): แยก 5 layer, use case ทำงานผ่าน repository interface

Stack: FastAPI · Pydantic v2 · SQLAlchemy 2 (async) · Alembic · SQLite / PostgreSQL · pytest

## Run

ใช้ [uv](https://docs.astral.sh/uv/) (Python 3.11+)

```bash
uv sync                              # สร้าง .venv + ติดตั้ง dependencies
cp .env.example .env                 # ค่า default ใช้ SQLite ไม่ต้องตั้งอะไร
uv run alembic upgrade head          # สร้างตาราง
uv run uvicorn src.main:app --reload # http://127.0.0.1:8000/docs
uv run pytest                        # 70 tests (unit + integration)
```

PostgreSQL:

```bash
docker compose up -d db
# .env: DATABASE_URL=postgresql+asyncpg://school:school@localhost:5432/school
uv run alembic upgrade head
```

หรือรันทั้งหมดใน Docker: `docker compose up --build` (API ที่ port 8000 รัน migration ให้อัตโนมัติ)

| Env | Default | |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./school.db` | async URL (`sqlite+aiosqlite` / `postgresql+asyncpg`) |
| `SQL_ECHO` | `false` | log SQL |
| `LOG_LEVEL` | `INFO` | |

สร้าง migration ใหม่หลังแก้ model: `uv run alembic revision --autogenerate -m "..."`

## Layers

```mermaid
flowchart LR
    Client --> P[Presentation<br/>routers · schemas · DI]
    P --> A[Application<br/>use cases · DTO · UnitOfWork]
    A --> D[Domain<br/>entities · rules · repository interfaces]
    I[Infrastructure<br/>SQLAlchemy models · repositories · Alembic] -. implements .-> D
    I --> DB[(Database)]
```

| Layer | Path | หน้าที่ | ไม่รู้จัก |
|---|---|---|---|
| Core | `src/core` | config, logging, error types (`NotFoundError`, `ConflictError`, `BusinessRuleError`) | — |
| Domain | `src/domain` | entities ตรวจความถูกต้องของตัวเอง, `Gender`, กฎ "ครูสอนได้เฉพาะห้องในโรงเรียนตัวเอง" (`Teacher.assign_classrooms`), repository ABC | FastAPI, SQLAlchemy, Pydantic |
| Application | `src/application` | use case ละ class (`CreateTeacher`, `GetSchoolDetail`, ...) ทำงานผ่าน `UnitOfWork` | FastAPI, SQLAlchemy |
| Infrastructure | `src/infrastructure` | ORM models, `SqlAlchemy*Repository`, `SqlAlchemyUnitOfWork`, migrations | FastAPI |
| Presentation | `src/presentation` | routers, Pydantic schemas, exception handlers | SQLAlchemy (ยกเว้น `dependencies/database.py` ซึ่งเป็น composition root ที่ผูก UnitOfWork เข้ากับ SQLAlchemy) |

## Endpoints

| Resource | List / Create | Get / PUT / PATCH / DELETE | Query filters | Detail เพิ่ม |
|---|---|---|---|---|
| School | `/api/v1/schools` | `/api/v1/schools/{id}` | `name` | `classroom_count`, `teacher_count`, `student_count` |
| Classroom | `/api/v1/classrooms` | `/api/v1/classrooms/{id}` | `school` | `teachers`, `students` |
| Teacher | `/api/v1/teachers` | `/api/v1/teachers/{id}` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classrooms` |
| Student | `/api/v1/students` | `/api/v1/students/{id}` | `school`, `classroom`, `firstname`, `lastname`, `gender` | `classroom` |

- ทุก list รับ `page` (default 1) และ `page_size` (default 20, สูงสุด 100) และตอบ `{"items": [...], "total", "page", "page_size"}`
- `name` / `firstname` / `lastname` = contains ไม่สนตัวพิมพ์ (`%`, `_` ถูก escape)
- PUT ต้องส่งครบทุก field; PATCH ส่งเฉพาะที่จะแก้ (ส่ง `null` = 422)
- ลบ school → ลบ classroom/teacher/student ตาม (FK `ON DELETE CASCADE`); ลบ classroom → ลบนักเรียนและการผูกครู

### Status codes / error format

| Status | เมื่อไร | `code` |
|---|---|---|
| 201 / 200 / 204 | create / read-update / delete | |
| 404 | ไม่พบ resource ใน URL | `not_found` |
| 409 | ห้อง (ชั้นปี/ทับ) ซ้ำในโรงเรียนเดียวกัน | `conflict` |
| 422 | body/query ผิดรูปแบบ | `validation_error` (+ `errors`) |
| 422 | ผิดกฎธุรกิจ เช่น อ้าง id ที่ไม่มี, ผูกครูกับห้องต่างโรงเรียน, ย้ายห้องที่มีครูไปโรงเรียนอื่น | `business_rule_violation` |

```json
{"detail": "Classrooms [3] do not belong to school 1", "code": "business_rule_violation"}
```

## ตัวอย่าง

```http
POST /api/v1/teachers
{"school_id": 1, "first_name": "Somchai", "last_name": "Jaidee", "gender": "M", "classroom_ids": [1]}

201 {"id": 1, "school_id": 1, "first_name": "Somchai", "last_name": "Jaidee", "gender": "M", "classroom_ids": [1]}
```

```http
GET /api/v1/schools/1

200 {"id": 1, "name": "Satit", "abbreviation": "SD", "address": "BKK",
     "classroom_count": 1, "teacher_count": 1, "student_count": 1}
```

```http
GET /api/v1/classrooms/1

200 {"id": 1, "school_id": 1, "year_level": 1, "section": "1",
     "teachers": [{"id": 1, "first_name": "Somchai", "last_name": "Jaidee", "gender": "M"}],
     "students": [{"id": 1, "first_name": "Mana", "last_name": "Dekdee", "gender": "M"}]}
```

## Query performance

- School detail: 1 query, 3 scalar subqueries (ไม่ JOIN classroom × teacher × student)
- Teacher: `classrooms` โหลดแบบ `selectin` (1 query ต่อทั้งหน้า ไม่ใช่ต่อครู)
- Teacher filter `classroom`: `EXISTS` บนตารางเชื่อม → ไม่มีแถวซ้ำ ไม่ต้อง `DISTINCT`
- Detail ทุกตัวใช้จำนวน query คงที่ ไม่ขึ้นกับจำนวนข้อมูล

## Tests

- `tests/unit/` — entity rules และ use case ด้วย `AsyncMock` repository (ไม่ใช้ DB)
- `tests/integration/` — เรียก HTTP จริงผ่าน `httpx.ASGITransport` บน SQLite in-memory (สร้างใหม่ทุก test) ครอบคลุม CRUD, ทุก filter, detail, pagination, validation, business rules, cascade delete

## โครงสร้าง

```text
fastapi-ddd-school/
├── src/
│   ├── main.py                      create_app()
│   ├── core/                        config.py, exceptions.py, logging.py
│   ├── domain/
│   │   ├── entities/                school.py, classroom.py, teacher.py, student.py
│   │   ├── value_objects/           gender.py, text.py
│   │   ├── repositories/            *_repository.py (ABC), criteria.py
│   │   └── services/
│   ├── application/
│   │   ├── use_cases/               base.py + {school,classroom,teacher,student}/{commands,queries}.py
│   │   ├── dto/                     inputs.py, details.py, pagination.py
│   │   └── unit_of_work.py
│   ├── infrastructure/
│   │   ├── db/                      base.py, session.py
│   │   ├── models/                  SQLAlchemy models + teacher_classrooms
│   │   ├── repositories/            SqlAlchemy*Repository, unit_of_work.py
│   │   └── migrations/              Alembic (versions/0001_initial_schema.py)
│   └── presentation/
│       ├── api/v1/                  schools.py, classrooms.py, teachers.py, students.py
│       ├── schemas/                 Pydantic request/response
│       ├── dependencies/            database.py (DI), pagination.py
│       └── exception_handlers.py
├── tests/{unit,integration}/
├── alembic.ini
├── pyproject.toml / uv.lock
├── Dockerfile
├── docker-compose.yml
└── README.md
```
