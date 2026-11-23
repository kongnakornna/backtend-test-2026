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
    queryset = School.objects.order_by("id")
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SchoolDetailSerializer
        return SchoolSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = (
        Classroom.objects.select_related("school")
        .prefetch_related("teachers__classrooms", "students")
        .order_by("id")
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
        .order_by("id")
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
        .order_by("id")
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentSerializer
