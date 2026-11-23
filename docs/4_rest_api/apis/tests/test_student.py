from rest_framework import status

from apis.models import Student
from apis.tests.base import BaseAPITestCase

URL = '/api/v1/students/'


class StudentAPITest(BaseAPITestCase):
    def test_create(self):
        response = self.client.post(
            URL,
            {'first_name': 'Chujai', 'last_name': 'Jaidee', 'gender': 'F', 'classroom': self.room_b1.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_requires_classroom(self):
        response = self.client.post(
            URL, {'first_name': 'Chujai', 'last_name': 'Jaidee', 'gender': 'F'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('classroom', response.data)

    def test_filter_school(self):
        response = self.client.get(URL, {'school': self.school_a.id})
        self.assertEqual(self.ids(response), [self.student_a.id, self.student_a2.id])

    def test_filter_classroom(self):
        self.assertEqual(self.ids(self.client.get(URL, {'classroom': self.room_b1.id})), [self.student_b.id])

    def test_filter_firstname(self):
        self.assertEqual(self.ids(self.client.get(URL, {'firstname': 'manee'})), [self.student_a2.id])

    def test_filter_lastname(self):
        self.assertEqual(self.ids(self.client.get(URL, {'lastname': 'yin'})), [self.student_b.id])

    def test_filter_gender(self):
        self.assertEqual(self.ids(self.client.get(URL, {'gender': 'F'})), [self.student_a2.id])

    def test_filter_combined(self):
        response = self.client.get(URL, {'school': self.school_a.id, 'gender': 'M'})
        self.assertEqual(self.ids(response), [self.student_a.id])

    def test_detail_shows_classroom(self):
        response = self.client.get(f'{URL}{self.student_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['classroom']['id'], self.room_a1.id)
        self.assertEqual(response.data['classroom']['school'], self.school_a.id)

    def test_move_classroom(self):
        response = self.client.patch(f'{URL}{self.student_a.id}/', {'classroom': self.room_a2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_a.refresh_from_db()
        self.assertEqual(self.student_a.classroom_id, self.room_a2.id)

    def test_delete(self):
        response = self.client.delete(f'{URL}{self.student_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Student.objects.filter(pk=self.student_b.id).exists())
