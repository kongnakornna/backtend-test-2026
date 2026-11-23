from rest_framework import status

from apis.models import Teacher
from apis.tests.base import BaseAPITestCase

URL = '/api/v1/teachers/'


class TeacherAPITest(BaseAPITestCase):
    def payload(self, **overrides):
        data = {
            'school': self.school_a.id,
            'first_name': 'Wichai',
            'last_name': 'Sukjai',
            'gender': 'M',
            'classrooms': [self.room_a1.id],
        }
        data.update(overrides)
        return data

    def test_create(self):
        response = self.client.post(URL, self.payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['classrooms'], [self.room_a1.id])

    def test_create_without_classrooms(self):
        response = self.client.post(URL, self.payload(classrooms=[]), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_rejects_classroom_of_other_school(self):
        response = self.client.post(URL, self.payload(classrooms=[self.room_b1.id]), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('classrooms', response.data)

    def test_create_invalid_gender(self):
        response = self.client.post(URL, self.payload(gender='X'), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_school(self):
        self.assertEqual(self.ids(self.client.get(URL, {'school': self.school_b.id})), [self.teacher_b.id])

    def test_filter_classroom(self):
        self.assertEqual(self.ids(self.client.get(URL, {'classroom': self.room_a2.id})), [self.teacher_a.id])

    def test_filter_firstname(self):
        self.assertEqual(self.ids(self.client.get(URL, {'firstname': 'som'})), [self.teacher_a.id])

    def test_filter_lastname(self):
        self.assertEqual(self.ids(self.client.get(URL, {'lastname': 'rak'})), [self.teacher_b.id])

    def test_filter_gender(self):
        self.assertEqual(self.ids(self.client.get(URL, {'gender': 'F'})), [self.teacher_b.id])

    def test_detail_lists_classrooms(self):
        response = self.client.get(f'{URL}{self.teacher_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [c['id'] for c in response.data['classrooms']], [self.room_a1.id, self.room_a2.id]
        )

    def test_update(self):
        response = self.client.put(
            f'{URL}{self.teacher_a.id}/', self.payload(first_name='Somsak', classrooms=[self.room_a2.id]),
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.teacher_a.refresh_from_db()
        self.assertEqual(self.teacher_a.first_name, 'Somsak')
        self.assertEqual(list(self.teacher_a.classrooms.values_list('id', flat=True)), [self.room_a2.id])

    def test_change_school_keeping_old_classrooms_is_rejected(self):
        response = self.client.patch(f'{URL}{self.teacher_a.id}/', {'school': self.school_b.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        response = self.client.delete(f'{URL}{self.teacher_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Teacher.objects.filter(pk=self.teacher_b.id).exists())
