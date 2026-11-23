from rest_framework import status
from rest_framework.test import APITestCase

from apis.models import Classroom, School, Student, Teacher


class ResourceAPITest(APITestCase):
    def setUp(self):
        self.school_a = School.objects.create(name="A", abbreviation="A", address="x")
        self.school_b = School.objects.create(name="B", abbreviation="B", address="y")
        self.room_a = Classroom.objects.create(
            school=self.school_a, year_level=1, section="1"
        )
        self.room_b = Classroom.objects.create(
            school=self.school_b, year_level=1, section="1"
        )

    def _teacher_payload(self, **overrides):
        payload = {
            "school": self.school_a.id,
            "first_name": "Somchai",
            "last_name": "Jaidee",
            "gender": "M",
            "classrooms": [self.room_a.id],
        }
        payload.update(overrides)
        return payload

    def test_duplicate_classroom_rejected(self):
        response = self.client.post(
            "/api/v1/classrooms/",
            {"school": self.school_a.id, "year_level": 1, "section": "1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_classroom_filter_by_school(self):
        response = self.client.get(f"/api/v1/classrooms/?school={self.school_b.id}")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.room_b.id)

    def test_classroom_detail_lists_teachers_and_students(self):
        teacher = Teacher.objects.create(
            school=self.school_a, first_name="T", last_name="L", gender="M"
        )
        teacher.classrooms.add(self.room_a)
        Student.objects.create(
            classroom=self.room_a, first_name="S", last_name="Q", gender="F"
        )

        response = self.client.get(f"/api/v1/classrooms/{self.room_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["teachers"]), 1)
        self.assertEqual(len(response.data["students"]), 1)

    def test_classroom_detail_query_count_is_constant(self):
        for i in range(10):
            teacher = Teacher.objects.create(
                school=self.school_a, first_name=f"T{i}", last_name="L", gender="M"
            )
            teacher.classrooms.add(self.room_a)

        # classroom+school, teachers, teachers' classrooms, students
        with self.assertNumQueries(4):
            self.client.get(f"/api/v1/classrooms/{self.room_a.id}/")

    def test_teacher_cannot_join_other_school_classroom(self):
        response = self.client.post(
            "/api/v1/teachers/",
            self._teacher_payload(classrooms=[self.room_b.id]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("classrooms", response.data)

    def test_teacher_invalid_gender_rejected(self):
        response = self.client.post(
            "/api/v1/teachers/", self._teacher_payload(gender="X"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teacher_school_change_validates_existing_classrooms(self):
        teacher_id = self.client.post(
            "/api/v1/teachers/", self._teacher_payload(), format="json"
        ).data["id"]
        response = self.client.patch(
            f"/api/v1/teachers/{teacher_id}/",
            {"school": self.school_b.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_teacher_filters_and_detail(self):
        teacher_id = self.client.post(
            "/api/v1/teachers/", self._teacher_payload(), format="json"
        ).data["id"]

        for query in [
            f"school={self.school_a.id}",
            f"classroom={self.room_a.id}",
            "firstname=somc",
            "lastname=JAI",
            "gender=m",
        ]:
            with self.subTest(query=query):
                response = self.client.get(f"/api/v1/teachers/?{query}")
                self.assertEqual(response.data["count"], 1)

        detail = self.client.get(f"/api/v1/teachers/{teacher_id}/").data
        self.assertEqual(detail["classrooms"][0]["id"], self.room_a.id)

    def test_student_filters_and_detail(self):
        student_id = self.client.post(
            "/api/v1/students/",
            {
                "classroom": self.room_a.id,
                "first_name": "Somsri",
                "last_name": "Dee",
                "gender": "F",
            },
            format="json",
        ).data["id"]

        for query in [
            f"school={self.school_a.id}",
            f"classroom={self.room_a.id}",
            "firstname=somsri",
            "lastname=dee",
            "gender=F",
        ]:
            with self.subTest(query=query):
                response = self.client.get(f"/api/v1/students/?{query}")
                self.assertEqual(response.data["count"], 1)

        response = self.client.get(f"/api/v1/students/?school={self.school_b.id}")
        self.assertEqual(response.data["count"], 0)

        detail = self.client.get(f"/api/v1/students/{student_id}/").data
        self.assertEqual(detail["classroom"]["id"], self.room_a.id)

    def test_update_and_delete_school_cascades(self):
        Student.objects.create(
            classroom=self.room_a, first_name="S", last_name="Q", gender="F"
        )
        response = self.client.patch(
            f"/api/v1/schools/{self.school_a.id}/", {"name": "A2"}, format="json"
        )
        self.assertEqual(response.data["name"], "A2")

        response = self.client.delete(f"/api/v1/schools/{self.school_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Student.objects.exists())
        self.assertFalse(Classroom.objects.filter(school_id=self.school_a.id).exists())
