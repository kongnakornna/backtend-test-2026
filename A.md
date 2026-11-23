 
# Project A: Django REST Framework

## A.1 โครงสร้างโปรเจกต์

```text
exam_app/
├── manage.py
├── requirements.txt
├── exam_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── apis/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── filters.py
    ├── models.py
    ├── serializers.py
    ├── urls.py
    ├── views.py
    └── tests/
        └── test_school.py
```

## A.2 `requirements.txt`

```txt
asgiref==3.8.1
Django==5.0.4
django-filter==24.2
djangorestframework==3.15.1
sqlparse==0.4.4
typing_extensions==4.11.0
```

## A.3 `apis/models.py`

```python
from django.db import models


class Gender(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    OTHER = "O", "Other"


class School(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50)
    address = models.TextField()

    def __str__(self) -> str:
        return self.name


class Classroom(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="classrooms",
    )
    year_level = models.PositiveSmallIntegerField()
    section = models.CharField(max_length=50)

    class Meta:
        unique_together = ("school", "year_level", "section")

    def __str__(self) -> str:
        return f"{self.school.abbreviation} {self.year_level}/{self.section}"


class Teacher(models.Model):
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="teachers",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    classrooms = models.ManyToManyField(
        Classroom,
        related_name="teachers",
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="students",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

## A.4 `apis/serializers.py`

```python
from rest_framework import serializers

from .models import Classroom, School, Student, Teacher


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "abbreviation", "address"]


class SchoolDetailSerializer(SchoolSerializer):
    classroom_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta(SchoolSerializer.Meta):
        fields = SchoolSerializer.Meta.fields + [
            "classroom_count",
            "teacher_count",
            "student_count",
        ]

    def get_classroom_count(self, obj: School) -> int:
        return obj.classrooms.count()

    def get_teacher_count(self, obj: School) -> int:
        return obj.teachers.count()

    def get_student_count(self, obj: School) -> int:
        return Student.objects.filter(classroom__school=obj).count()


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["id", "school", "year_level", "section"]


class TeacherSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Classroom.objects.all(),
        required=False,
    )

    class Meta:
        model = Teacher
        fields = [
            "id",
            "school",
            "first_name",
            "last_name",
            "gender",
            "classrooms",
        ]

    def validate(self, attrs):
        school = attrs.get("school") or getattr(self.instance, "school", None)
        classrooms = attrs.get("classrooms")

        if classrooms is None and self.instance:
            classrooms = self.instance.classrooms.all()

        if school and classrooms:
            for classroom in classrooms:
                if classroom.school_id != school.id:
                    raise serializers.ValidationError(
                        {
                            "classrooms": (
                                "All classrooms must belong to the same school."
                            )
                        }
                    )

        return attrs


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "id",
            "classroom",
            "first_name",
            "last_name",
            "gender",
        ]


class ClassroomDetailSerializer(ClassroomSerializer):
    teachers = TeacherSerializer(many=True, read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = ClassroomSerializer.Meta.fields + ["teachers", "students"]


class TeacherDetailSerializer(TeacherSerializer):
    classrooms = ClassroomSerializer(many=True, read_only=True)

    class Meta(TeacherSerializer.Meta):
        fields = TeacherSerializer.Meta.fields


class StudentDetailSerializer(StudentSerializer):
    classroom = ClassroomSerializer(read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields
```

## A.5 `apis/filters.py`

```python
from django_filters import FilterSet, filters

from .models import Classroom, School, Student, Teacher


class SchoolFilter(FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = School
        fields = ["name"]


class ClassroomFilter(FilterSet):
    school = filters.NumberFilter(field_name="school__id")

    class Meta:
        model = Classroom
        fields = ["school"]


class TeacherFilter(FilterSet):
    school = filters.NumberFilter(field_name="school__id")
    classroom = filters.NumberFilter(field_name="classrooms__id")
    firstname = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    lastname = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    gender = filters.CharFilter(field_name="gender")

    class Meta:
        model = Teacher
        fields = ["school", "classroom", "firstname", "lastname", "gender"]


class StudentFilter(FilterSet):
    school = filters.NumberFilter(field_name="classroom__school__id")
    classroom = filters.NumberFilter(field_name="classroom__id")
    firstname = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    lastname = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    gender = filters.CharFilter(field_name="gender")

    class Meta:
        model = Student
        fields = ["school", "classroom", "firstname", "lastname", "gender"]
```

## A.6 `apis/views.py`

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .filters import (
    ClassroomFilter,
    SchoolFilter,
    StudentFilter,
    TeacherFilter,
)
from .models import Classroom, School, Student, Teacher
from .serializers import (
    ClassroomDetailSerializer,
    ClassroomSerializer,
    SchoolDetailSerializer,
    SchoolSerializer,
    StudentDetailSerializer,
    StudentSerializer,
    TeacherDetailSerializer,
    TeacherSerializer,
)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SchoolDetailSerializer
        return SchoolSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = (
        Classroom.objects.select_related("school")
        .prefetch_related("teachers", "students")
        .all()
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClassroomFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ClassroomDetailSerializer
        return ClassroomSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = (
        Teacher.objects.select_related("school")
        .prefetch_related("classrooms")
        .all()
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = TeacherFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeacherDetailSerializer
        return TeacherSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = (
        Student.objects.select_related("classroom", "classroom__school")
        .all()
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentSerializer
```

## A.7 `apis/urls.py`

```python
from rest_framework.routers import DefaultRouter

from .views import ClassroomViewSet, SchoolViewSet, StudentViewSet, TeacherViewSet

router = DefaultRouter()
router.register("schools", SchoolViewSet, basename="school")
router.register("classrooms", ClassroomViewSet, basename="classroom")
router.register("teachers", TeacherViewSet, basename="teacher")
router.register("students", StudentViewSet, basename="student")

urlpatterns = router.urls
```

## A.8 `exam_app/urls.py`

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apis.urls")),
]
```

## A.9 `apis/tests/test_school.py`

```python
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apis.models import Classroom, School, Student, Teacher


class SchoolAPITest(APITestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Demo School",
            abbreviation="DS",
            address="Bangkok",
        )

    def test_create_school(self):
        url = "/api/v1/schools/"
        response = self.client.post(
            url,
            {
                "name": "New School",
                "abbreviation": "NS",
                "address": "Chiang Mai",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(School.objects.count(), 2)

    def test_school_filter_by_name(self):
        url = "/api/v1/schools/?name=Demo"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_school_detail_counts(self):
        classroom = Classroom.objects.create(
            school=self.school,
            year_level=1,
            section="A",
        )
        Teacher.objects.create(
            school=self.school,
            first_name="Somchai",
            last_name="Jaidee",
            gender="M",
        )
        Student.objects.create(
            classroom=classroom,
            first_name="Somsri",
            last_name="Dee",
            gender="F",
        )

        url = f"/api/v1/schools/{self.school.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["classroom_count"], 1)
        self.assertEqual(response.data["teacher_count"], 1)
        self.assertEqual(response.data["student_count"], 1)
```

## A.10 คำสั่งรัน Django

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

---

# Project B: FastAPI DDD Starter

> ส่วนนี้เป็น **starter ที่รันได้จริง** สำหรับ module `school` และมีโครงสร้าง DDD ครบ layer ส่วน `classroom/teacher/student` ให้สร้างตาม pattern เดียวกัน

##  โครงสร้าง

```text
fastapi-ddd-school/
├── requirements.txt
├── src/
│   ├── core/
│   │   └── config.py
│   ├── domain/
│   │   ├── entities.py
│   │   └── repositories.py
│   ├── infrastructure/
│   │   ├── db/
│   │   │   └── session.py
│   │   ├── models.py
│   │   └── repositories/
│   │       └── school_repository.py
│   ├── application/
│   │   └── use_cases/
│   │       └── school.py
│   ├── presentation/
│   │   ├── schemas/
│   │   │   └── school.py
│   │   └── api/
│   │       └── v1/
│   │           └── schools.py
│   └── main.py
```

## B.2 `requirements.txt`

```txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
pydantic-settings==2.2.1
alembic==1.13.1
```
 