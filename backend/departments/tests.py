from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from departments.models import Department

class DepartmentModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            role='admin'
        )

    def test_department_crud(self):
        self.client.login(username='admin_test', password='testpassword123')
        
        # 1. Add
        data = {'name': 'Civil Engineering', 'code': 'CIVIL', 'description': 'Civil Dept'}
        res = self.client.post(reverse('department_add'), data)
        self.assertRedirects(res, reverse('department_list'))
        dept = Department.objects.get(code='CIVIL')
        self.assertEqual(dept.name, 'Civil Engineering')

        # 2. Edit
        edit_data = {'name': 'Civil & Environmental Engineering', 'code': 'CIVIL', 'description': 'Updated'}
        res = self.client.post(reverse('department_edit', args=[dept.pk]), edit_data)
        self.assertRedirects(res, reverse('department_list'))
        dept.refresh_from_db()
        self.assertEqual(dept.name, 'Civil & Environmental Engineering')

        # 3. Delete
        res = self.client.get(reverse('department_delete', args=[dept.pk]))
        self.assertRedirects(res, reverse('department_list'))
        self.assertFalse(Department.objects.filter(pk=dept.pk).exists())

