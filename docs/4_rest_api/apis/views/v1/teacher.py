from rest_framework import viewsets

from apis.filters import TeacherFilter
from apis.models import Teacher
from apis.serializers import TeacherDetailSerializer, TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    filterset_class = TeacherFilter
    queryset = Teacher.objects.select_related('school').prefetch_related('classrooms')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeacherDetailSerializer
        return TeacherSerializer
