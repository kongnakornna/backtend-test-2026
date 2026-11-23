from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apis.models import Classroom, School, Student, Teacher


class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username='tester', password='pass1234')

        cls.school_a = School.objects.create(name='Satit Demo', abbreviation='SD', address='Bangkok')
        cls.school_b = School.objects.create(name='Triam Udom', abbreviation='TU', address='Bangkok')

        cls.room_a1 = Classroom.objects.create(school=cls.school_a, year_level=1, section='1')
        cls.room_a2 = Classroom.objects.create(school=cls.school_a, year_level=1, section='2')
        cls.room_b1 = Classroom.objects.create(school=cls.school_b, year_level=4, section='1')

        cls.teacher_a = Teacher.objects.create(
            school=cls.school_a, first_name='Somchai', last_name='Jaidee', gender='M'
        )
        cls.teacher_a.classrooms.set([cls.room_a1, cls.room_a2])
        cls.teacher_b = Teacher.objects.create(
            school=cls.school_b, first_name='Suda', last_name='Rakdee', gender='F'
        )
        cls.teacher_b.classrooms.set([cls.room_b1])

        cls.student_a = Student.objects.create(
            classroom=cls.room_a1, first_name='Mana', last_name='Dekdee', gender='M'
        )
        cls.student_a2 = Student.objects.create(
            classroom=cls.room_a2, first_name='Manee', last_name='Meejai', gender='F'
        )
        cls.student_b = Student.objects.create(
            classroom=cls.room_b1, first_name='Piti', last_name='Yindee', gender='M'
        )

    def setUp(self):
        self.client.force_authenticate(self.user)
        # BrowsableAPIRenderer is listed first in settings and rewrites 204 -> 200
        # for HTML display, so ask for JSON like a real API client would.
        self.client.credentials(HTTP_ACCEPT='application/json')

    @staticmethod
    def ids(response):
        return [item['id'] for item in response.data['results']]
