# AI Prompts

## 1. Master prompt — FastAPI DDD

```text
คุณเป็น Senior Backend Engineer ที่เชี่ยวชาญ FastAPI, DDD, SQLAlchemy 2.0, Alembic, Pydantic v2 และการออกแบบ REST API

เป้าหมาย:
สร้างโปรเจกต์ FastAPI ตามแนวทาง https://github.com/CodesForge/fastapi-ddd-template สำหรับระบบจัดการโรงเรียนและบุคลากร

Entities:
- School: name, abbreviation, address
- Classroom: year_level, section, school
- Teacher: first_name, last_name, gender (M/F/O), school, classrooms (many-to-many)
- Student: first_name, last_name, gender (M/F/O), classroom

ความสัมพันธ์และกฎ:
- School 1:N Classroom, School 1:N Teacher, Teacher M:N Classroom, Classroom 1:N Student
- Teacher กับ Classroom ที่ผูกกันต้องอยู่ School เดียวกัน (ตรวจตอนสร้าง, แก้ไขห้อง, เปลี่ยนโรงเรียน, ย้ายห้องไปโรงเรียนอื่น)
- (school, year_level, section) ต้อง unique, year_level >= 1

API (prefix /api/v1):
- schools: CRUD, filter name, detail มี classroom_count / teacher_count / student_count
- classrooms: CRUD, filter school, detail มี teachers และ students
- teachers: CRUD, filter school / classroom / firstname / lastname / gender, detail มี classrooms
- students: CRUD, filter school / classroom / firstname / lastname / gender, detail มี classroom

ข้อกำหนดทางสถาปัตยกรรม:
- แยก layer: core, domain, application, infrastructure, presentation
- Domain ไม่ import FastAPI / SQLAlchemy / Pydantic
- Application ใช้ use case + repository interface (+ Unit of Work)
- Infrastructure implement repository ด้วย SQLAlchemy async
- Presentation ใช้ FastAPI router + Pydantic schema + Depends สำหรับ DI
- Alembic migration, pagination, exception handler ที่แปลง domain error เป็น HTTP status
- Eager loading (selectinload / joinedload) ป้องกัน N+1; count ใน school detail ใช้ subquery
- pytest: unit test (domain + use case ด้วย fake repository) และ integration test (API + DB)
- README: วิธี run, migration, test, ตัวอย่าง request/response

ผลลัพธ์ที่ต้องการ:
1. โครงสร้างโฟลเดอร์ทั้งหมด
2. โค้ดไฟล์สำคัญให้ครบ
3. เหตุผลการออกแบบสั้น ๆ
4. สิ่งที่ต้องตั้งค่าเพิ่ม เช่น DATABASE_URL
5. ถ้า requirement ใดไม่ชัดเจน ให้ถามกลับก่อน ไม่ต้องเดา
```

## 2. Prompt — Django REST Framework (Part 4)

```text
คุณเป็น Senior Django Developer ที่เชี่ยวชาญ Django REST Framework, django-filter และการออกแบบ API

เป้าหมาย:
ใน project Django ที่มีอยู่แล้ว (exam_app, app ชื่อ apis, Django 5.0, DRF 3.15, django-filter 24.2, Python 3.10–3.12)
พัฒนา API ระบบจัดการโรงเรียนและบุคลากรตาม 4_rest_api/api_exam.md โดยใช้โครงไฟล์เดิม:
apis/models.py, serializers.py, filters.py, views/v1/*.py, urls.py (DefaultRouter, prefix /api/v1/)

Models:
- School: name, abbreviation, address
- Classroom: year_level, section, school FK  (unique: school + year_level + section)
- Teacher: first_name, last_name, gender, school FK, classrooms M2M
- Student: first_name, last_name, gender, classroom FK

API:
- schools: CRUD, filter name, detail มี classroom_count / teacher_count / student_count
- classrooms: CRUD, filter school, detail มี teachers และ students
- teachers: CRUD, filter school / classroom / firstname / lastname / gender, detail มี classrooms
- students: CRUD, filter school / classroom / firstname / lastname / gender, detail มี classroom

ข้อกำหนด:
- ModelViewSet + get_serializer_class แยก serializer สำหรับ list/write กับ detail
- FilterSet ของ django_filter สำหรับทุก filter (query param ชื่อ firstname / lastname ตามโจทย์)
- validate ว่า teacher ผูกได้เฉพาะ classroom ในโรงเรียนเดียวกัน
- select_related / prefetch_related; count ด้วย subquery ไม่ใช่ JOIN หลายตาราง
- PageNumberPagination
- tests ด้วย APITestCase: CRUD, ทุก filter, detail, validation (settings ใช้ IsAuthenticated)
- README วิธี run และตัวอย่าง request/response

ถ้ามีจุดที่ requirement ไม่ชัดเจน ให้ถามกลับก่อน
```

## 3. Follow-up prompt — review

```text
ช่วย review โค้ดนี้ในมุม Senior Backend Engineer:
- โครงสร้าง layer (DDD) มีจุดไหนรั่ว เช่น router เรียก ORM ตรง หรือ domain import framework
- N+1 query และ query ที่ JOIN แล้วแถวระเบิด
- validation และ business rule (โดยเฉพาะ teacher-classroom ต้องอยู่ school เดียวกัน ทั้งตอน create และ update)
- filter ครบตาม requirement และให้ผลถูกต้องกับ M2M (distinct)
- serializer/schema ของ list และ detail เหมาะสม
- error handling และ status code
- test coverage ที่ยังขาด
เสนอ patch เป็น diff พร้อมอธิบายเหตุผล
```
