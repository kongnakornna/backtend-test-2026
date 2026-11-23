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
