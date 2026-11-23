from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from rest_framework import viewsets

from apis.filters import SchoolFilter
from apis.models import Classroom, School, Student, Teacher
from apis.serializers import SchoolDetailSerializer, SchoolSerializer


def _count_by_school(queryset, school_field):
    """Correlated COUNT subquery per school.

    Separate subqueries avoid the row explosion that JOINing classrooms,
    teachers and students together would cause with Count(distinct=True).
    """
    counts = (
        queryset.filter(**{school_field: OuterRef('pk')})
        .order_by()
        .values(school_field)
        .annotate(total=Count('pk'))
        .values('total')
    )
    return Coalesce(Subquery(counts, output_field=IntegerField()), 0)


class SchoolViewSet(viewsets.ModelViewSet):
    filterset_class = SchoolFilter

    def get_queryset(self):
        queryset = School.objects.all()
        if self.action == 'retrieve':
            queryset = queryset.annotate(
                classroom_count=_count_by_school(Classroom.objects.all(), 'school'),
                teacher_count=_count_by_school(Teacher.objects.all(), 'school'),
                student_count=_count_by_school(Student.objects.all(), 'classroom__school'),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SchoolDetailSerializer
        return SchoolSerializer
