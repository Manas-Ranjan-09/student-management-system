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

    def test_admin_profile_photo_upload_and_removal(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='admin_test', password='testpassword123')
        
        # Test upload with action='stay'
        photo = SimpleUploadedFile("avatar.jpg", b"fake_image_bytes", content_type="image/jpeg")
        data = {
            'name': 'Admin With Photo',
            'email': 'admin@test.com',
            'designation': 'IT Lead',
            'profile_photo': photo,
            'action': 'stay'
        }
        response = self.client.post(reverse('admin_profile'), data)
        self.assertRedirects(response, reverse('admin_profile'))
        
        self.admin_user.refresh_from_db()
        self.assertTrue(bool(self.admin_user.admin_profile.profile_photo))
        self.assertIn('avatar', self.admin_user.admin_profile.profile_photo.name)
        
        # Test photo removal
        data_remove = {
            'name': 'Admin With Photo',
            'email': 'admin@test.com',
            'designation': 'IT Lead',
            'remove_photo': 'true',
            'action': 'stay'
        }
        response_remove = self.client.post(reverse('admin_profile'), data_remove)
        self.assertRedirects(response_remove, reverse('admin_profile'))
        
        self.admin_user.refresh_from_db()
        self.assertFalse(bool(self.admin_user.admin_profile.profile_photo))

    def test_department_detail_view(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('department_detail', args=[self.dept.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student_profile.name)

    def test_login_view_get_unauthenticated(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_login_view_post_without_remember_me(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'testpassword123'
        })
        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)
        session = self.client.session
        self.assertFalse(session.get('remember_me'))
        self.assertTrue(session.get_expire_at_browser_close())

    def test_login_view_post_with_remember_me(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'testpassword123',
            'remember_me': 'on'
        })
        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)
        session = self.client.session
        self.assertTrue(session.get('remember_me'))
        self.assertFalse(session.get_expire_at_browser_close())
        self.assertGreater(session.get_expiry_age(), 0)

    def test_login_view_authenticated_without_remember_me_logs_out(self):
        # Log in without remember_me
        self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'testpassword123'
        })
        # Reopening the main link without remember_me should flush session and show login
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        # Check that user is logged out
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_view_authenticated_with_remember_me_redirects(self):
        # Log in with remember_me
        self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'testpassword123',
            'remember_me': 'on'
        })
        # Reopening the link with remember_me should redirect to dashboard
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard_redirect'), target_status_code=302)


    def test_logout_view(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

