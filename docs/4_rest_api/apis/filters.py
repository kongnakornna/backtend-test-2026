from django_filters import FilterSet, filters

from apis.models import Classroom, Gender, School, Student, Teacher


class SchoolFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = School
        fields = ['name']


class ClassroomFilter(FilterSet):
    school = filters.ModelChoiceFilter(queryset=School.objects.all())

    class Meta:
        model = Classroom
        fields = ['school']


class TeacherFilter(FilterSet):
    school = filters.ModelChoiceFilter(queryset=School.objects.all())
    classroom = filters.ModelChoiceFilter(
        field_name='classrooms', queryset=Classroom.objects.all(), distinct=True
    )
    firstname = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    lastname = filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(choices=Gender.choices)

    class Meta:
        model = Teacher
        fields = ['school', 'classroom', 'firstname', 'lastname', 'gender']


class StudentFilter(FilterSet):
    school = filters.ModelChoiceFilter(field_name='classroom__school', queryset=School.objects.all())
    classroom = filters.ModelChoiceFilter(queryset=Classroom.objects.all())
    firstname = filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    lastname = filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    gender = filters.ChoiceFilter(choices=Gender.choices)

    class Meta:
        model = Student
        fields = ['school', 'classroom', 'firstname', 'lastname', 'gender']
