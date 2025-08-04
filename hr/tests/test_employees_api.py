from django.urls import reverse
from rest_framework import status
from rest_framework.test import (
    APIClient,
    APITestCase,
)

from hr.models import Employee, Position
from hr.tests.factories import (
    EmployeeFactory,
    PositionFactory,
    DepartmentFactory,
)


class EmployeeAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Employee.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.position = PositionFactory()
        self.client.force_authenticate(user=self.user)

    def test_get_employee_list(self):
        response = self.client.get(reverse('api-hr:employee-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_employee(self):
        data = {
            'username': 'newemployee',
            'first_name': 'Test',
            'last_name': 'Employee',
            'email': 'test@employee.com',
            'position': self.position.pk,
        }
        response = self.client.post(reverse('api-hr:employee-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_employee(self):
        employee = EmployeeFactory(position=self.position)
        data = {'first_name': 'Updated Name'}
        response = self.client.patch(reverse('api-hr:employee-detail', kwargs={'pk': employee.pk}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_employee(self):
        employee = EmployeeFactory(position=self.position)
        response = self.client.delete(reverse('api-hr:employee-detail', kwargs={'pk': employee.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_search_employee(self):
        response = self.client.get(reverse('api-hr:employee-list'), {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PositionViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = EmployeeFactory(is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=self.user)

        self.department = DepartmentFactory()
        self.position = PositionFactory(department=self.department)

    def test_get_position_list(self):
        url = reverse('api-hr:position-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_get_position_detail(self):
        url = reverse('api-hr:position-detail', kwargs={'pk': self.position.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.position.pk)

    def test_create_position(self):
        url = reverse('api-hr:position-list')
        data = {
            'title': 'New Position',
            'department': self.department.pk,
            'is_manager': False,
            'is_active': True,
            'job_description': 'Description for new position',
            'monthly_rate': '1000.00',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Position.objects.filter(title='New Position').exists())


    def test_update_position(self):
        url = reverse('api-hr:position-detail', kwargs={'pk': self.position.pk})
        data = {
            'title': 'Updated Position Title',
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.position.refresh_from_db()
        self.assertEqual(self.position.title, 'Updated Position Title')

    def test_delete_position(self):
        url = reverse('api-hr:position-detail', kwargs={'pk': self.position.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Position.objects.filter(pk=self.position.pk).exists())
