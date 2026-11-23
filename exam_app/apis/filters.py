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
    gender = filters.CharFilter(field_name="gender", lookup_expr="iexact")

    class Meta:
        model = Teacher
        fields = ["school", "classroom", "firstname", "lastname", "gender"]


class StudentFilter(FilterSet):
    school = filters.NumberFilter(field_name="classroom__school__id")
    classroom = filters.NumberFilter(field_name="classroom__id")
    firstname = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    lastname = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    gender = filters.CharFilter(field_name="gender", lookup_expr="iexact")

    class Meta:
        model = Student
        fields = ["school", "classroom", "firstname", "lastname", "gender"]
