from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from departments.models import Department
from courses.models import Course
from students.models import Student

class StudentModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            role='admin'
        )
        self.dept = Department.objects.create(name='Mechanical Engineering', code='ME')
        self.course = Course.objects.create(name='B.Tech ME', code='BTECHME', duration='4 Years')
        
        self.student_user = User.objects.create_user(
            username='2026ME001',
            email='studentme@test.com',
            password='testpassword123',
            role='student'
        )
        self.student = Student.objects.create(
            student_id='STUME001',
            user=self.student_user,
            roll_number='2026ME001',
            registration_number='REGME001',
            name='Test Student ME',
            email='studentme@test.com',
            phone='9876543210',
            gender='Male',
            dob='2002-01-01',
            address='123 Tech Campus',
            department=self.dept,
            course=self.course,
            semester=1,
            academic_year='2026-2030'
        )

    def test_student_list_authenticated_admin(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Student ME')

    def test_student_detail_view(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('student_detail', args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Student ME')
        self.assertContains(response, 'Overall CGPA')

    def test_student_add(self):
        self.client.login(username='admin_test', password='testpassword123')
        data = {
            'student_id': 'STUME002',
            'name': 'Second Student ME',
            'roll_number': '2026ME002',
            'registration_number': 'REGME002',
            'email': 'studentme2@test.com',
            'phone': '9876543211',
            'gender': 'Female',
            'dob': '2002-02-02',
            'address': '456 Tech Campus',
            'department': self.dept.pk,
            'course': self.course.pk,
            'semester': 1,
            'academic_year': '2026-2030',
            'admission_date': '2026-08-01',
            'password': 'password123'
        }
        response = self.client.post(reverse('student_add'), data)
        self.assertRedirects(response, reverse('student_list'))
        self.assertTrue(Student.objects.filter(student_id='STUME002').exists())
        self.assertTrue(User.objects.filter(username='2026ME002').exists())

    def test_student_edit(self):
        self.client.login(username='admin_test', password='testpassword123')
        data = {
            'name': 'Updated Student ME',
            'registration_number': 'REGME001',
            'email': 'updatedme@test.com',
            'phone': '9876543210',
            'gender': 'Male',
            'dob': '2002-01-01',
            'address': 'New Address 456',
            'department': self.dept.pk,
            'course': self.course.pk,
            'semester': 2,
            'academic_year': '2026-2030',
            'admission_date': '2026-08-01'
        }
        response = self.client.post(reverse('student_edit', args=[self.student.pk]), data)
        self.assertRedirects(response, reverse('student_list'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.name, 'Updated Student ME')
        self.assertEqual(self.student.semester, 2)

    def test_student_delete(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('student_delete', args=[self.student.pk]))
        self.assertRedirects(response, reverse('student_list'))
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())
        self.assertFalse(User.objects.filter(pk=self.student_user.pk).exists())

