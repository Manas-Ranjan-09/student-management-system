from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from courses.models import Course

class CourseModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            role='admin'
        )

    def test_course_crud(self):
        self.client.login(username='admin_test', password='testpassword123')
        
        # 1. Add
        data = {'name': 'Bachelor of Design', 'code': 'BDES', 'duration': '4 Years', 'description': 'Design'}
        res = self.client.post(reverse('course_add'), data)
        self.assertRedirects(res, reverse('course_list'))
        course = Course.objects.get(code='BDES')
        self.assertEqual(course.name, 'Bachelor of Design')

        # 2. Edit
        edit_data = {'name': 'Bachelor of Design (Hons)', 'code': 'BDES', 'duration': '4 Years', 'description': 'Updated'}
        res = self.client.post(reverse('course_edit', args=[course.pk]), edit_data)
        self.assertRedirects(res, reverse('course_list'))
        course.refresh_from_db()
        self.assertEqual(course.name, 'Bachelor of Design (Hons)')

        # 3. Delete
        res = self.client.get(reverse('course_delete', args=[course.pk]))
        self.assertRedirects(res, reverse('course_list'))
        self.assertFalse(Course.objects.filter(pk=course.pk).exists())

