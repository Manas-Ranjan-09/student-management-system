from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from departments.models import Department
from courses.models import Course
from students.models import Student

class AuthRoutingTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Create Admin
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            role='admin'
        )
        
        # 2. Create Student
        self.student_user = User.objects.create_user(
            username='student_test',
            email='student@test.com',
            password='testpassword123',
            role='student'
        )
        
        # Create department & course dependencies for student profile
        self.dept = Department.objects.create(name='Computer Science', code='CS')
        self.course = Course.objects.create(name='B.Tech', code='BTECH', duration='4 Years')
        
        self.student_profile = Student.objects.create(
            student_id='STU001',
            user=self.student_user,
            roll_number='student_test',
            registration_number='REG001',
            name='Test Student',
            email='student@test.com',
            phone='1234567890',
            gender='Male',
            dob='2000-01-01',
            address='Test Address',
            department=self.dept,
            course=self.course,
            semester=1,
            academic_year='2026-2030'
        )

    def test_anonymous_redirect(self):
        # Anonymous users accessing dashboards should be redirected to login
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('admin_dashboard')}")
        
        response = self.client.get(reverse('student_dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('student_dashboard')}")

    def test_admin_dashboard_access_allowed_for_admin(self):
        # Log in as admin
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_access_denied_for_student(self):
        # Log in as student
        self.client.login(username='student_test', password='testpassword123')
        # Expect permission denied (403)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_student_dashboard_access_allowed_for_student(self):
        # Log in as student
        self.client.login(username='student_test', password='testpassword123')
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_student_dashboard_access_denied_for_admin(self):
        # Log in as admin
        self.client.login(username='admin_test', password='testpassword123')
        # Expect permission denied (403)
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_redirect_admin(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_dashboard_redirect_student(self):
        self.client.login(username='student_test', password='testpassword123')
        response = self.client.get(reverse('dashboard_redirect'))
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_student_self_registration(self):
        data = {
            'student_id': 'STU_NEW_001',
            'name': 'New Student Self',
            'roll_number': '2026NEW001',
            'registration_number': 'REGNEW001',
            'email': 'newself@student.com',
            'phone': '1234567890',
            'gender': 'Female',
            'dob': '2004-06-18',
            'address': 'New Address',
            'department': self.dept.id,
            'course': self.course.id,
            'semester': 1,
            'academic_year': '2026-2030',
            'admission_date': '2026-08-01',
            'password': 'strongpassword123',
            'confirm_password': 'strongpassword123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('login'))
        
        self.assertTrue(User.objects.filter(username='2026NEW001').exists())
        self.assertTrue(Student.objects.filter(roll_number='2026NEW001').exists())

    def test_admin_profile_view_get(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('admin_profile'))
        self.assertEqual(response.status_code, 200)

    def test_admin_profile_view_post(self):
        self.client.login(username='admin_test', password='testpassword123')
        data = {
            'name': 'Updated System Admin Name',
            'email': 'updated_admin@test.com',
            'phone': '9876543210',
            'designation': 'Registrar Director'
        }
        response = self.client.post(reverse('admin_profile'), data)
        self.assertRedirects(response, reverse('admin_dashboard'))
        
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.email, 'updated_admin@test.com')
        self.assertEqual(self.admin_user.admin_profile.name, 'Updated System Admin Name')
        self.assertEqual(self.admin_user.admin_profile.designation, 'Registrar Director')

    def test_department_detail_view(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('department_detail', args=[self.dept.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student_profile.name)

