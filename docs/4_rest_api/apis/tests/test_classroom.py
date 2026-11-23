from rest_framework import status

from apis.models import Classroom
from apis.tests.base import BaseAPITestCase

URL = '/api/v1/classrooms/'


class ClassroomAPITest(BaseAPITestCase):
    def test_create(self):
        response = self.client.post(
            URL, {'school': self.school_a.id, 'year_level': 2, 'section': '1'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_requires_school(self):
        response = self.client.post(URL, {'year_level': 2, 'section': '1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('school', response.data)

    def test_create_duplicate_in_same_school(self):
        response = self.client.post(
            URL, {'school': self.school_a.id, 'year_level': 1, 'section': '1'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_year_level(self):
        response = self.client.post(
            URL, {'school': self.school_a.id, 'year_level': 0, 'section': '9'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_school(self):
        response = self.client.get(URL, {'school': self.school_a.id})
        self.assertEqual(self.ids(response), [self.room_a1.id, self.room_a2.id])

    def test_detail_lists_teachers_and_students(self):
        response = self.client.get(f'{URL}{self.room_a1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([t['id'] for t in response.data['teachers']], [self.teacher_a.id])
        self.assertEqual([s['id'] for s in response.data['students']], [self.student_a.id])
        self.assertEqual(response.data['school']['id'], self.school_a.id)

    def test_update(self):
        response = self.client.patch(f'{URL}{self.room_a2.id}/', {'section': '3'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['section'], '3')

    def test_cannot_move_to_school_of_different_teachers(self):
        response = self.client.patch(f'{URL}{self.room_a1.id}/', {'school': self.school_b.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        response = self.client.delete(f'{URL}{self.room_b1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Classroom.objects.filter(pk=self.room_b1.id).exists())
