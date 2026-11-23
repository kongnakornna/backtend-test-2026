from rest_framework import status

from apis.models import School
from apis.tests.base import BaseAPITestCase

URL = '/api/v1/schools/'


class SchoolAPITest(BaseAPITestCase):
    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(URL).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create(self):
        response = self.client.post(URL, {'name': 'New', 'abbreviation': 'NW', 'address': 'CNX'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(School.objects.filter(name='New').exists())

    def test_create_missing_field(self):
        response = self.client.post(URL, {'name': 'New'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('abbreviation', response.data)

    def test_list_is_paginated(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_name(self):
        response = self.client.get(URL, {'name': 'triam'})
        self.assertEqual(self.ids(response), [self.school_b.id])

    def test_detail_counts(self):
        response = self.client.get(f'{URL}{self.school_a.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['classroom_count'], 2)
        self.assertEqual(response.data['teacher_count'], 1)
        self.assertEqual(response.data['student_count'], 2)

    def test_detail_counts_empty_school(self):
        school = School.objects.create(name='Empty', abbreviation='E', address='-')
        response = self.client.get(f'{URL}{school.id}/')
        self.assertEqual(
            (response.data['classroom_count'], response.data['teacher_count'], response.data['student_count']),
            (0, 0, 0),
        )

    def test_detail_not_found(self):
        self.assertEqual(self.client.get(f'{URL}9999/').status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        response = self.client.put(
            f'{URL}{self.school_a.id}/', {'name': 'Renamed', 'abbreviation': 'RN', 'address': 'BKK'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.school_a.refresh_from_db()
        self.assertEqual(self.school_a.name, 'Renamed')

    def test_partial_update(self):
        response = self.client.patch(f'{URL}{self.school_a.id}/', {'address': 'Nonthaburi'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], 'Nonthaburi')

    def test_delete(self):
        response = self.client.delete(f'{URL}{self.school_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(School.objects.filter(pk=self.school_b.id).exists())
