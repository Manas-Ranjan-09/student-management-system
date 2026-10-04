from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from accounts.models import User
from departments.models import Department
from courses.models import Course
from students.models import Student
from results.models import SemesterResult

class ResultModuleTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpassword123',
            role='admin'
        )
        self.dept = Department.objects.create(name='Electrical Engineering', code='EE')
        self.course = Course.objects.create(name='B.Tech EE', code='BTECHEE', duration='4 Years')
        
        self.student_user = User.objects.create_user(
            username='2026EE001',
            email='studentee@test.com',
            password='testpassword123',
            role='student'
        )
        self.student = Student.objects.create(
            student_id='STUEE001',
            user=self.student_user,
            roll_number='2026EE001',
            registration_number='REGEE001',
            name='Test Student EE',
            email='studentee@test.com',
            phone='9876543210',
            gender='Female',
            dob='2003-03-03',
            address='789 Circuit Way',
            department=self.dept,
            course=self.course,
            semester=1,
            academic_year='2026-2030'
        )
        
        self.result = SemesterResult.objects.create(
            student=self.student,
            semester=1,
            subject_name='Circuit Analysis',
            subject_code='EE-101',
            internal_marks=Decimal('28.00'),
            external_marks=Decimal('62.00'),
            credit=4
        )

    def test_result_auto_calculations(self):
        self.assertEqual(self.result.total, Decimal('90.00'))
        self.assertEqual(self.result.grade, 'A+')
        self.assertEqual(self.result.result_status, 'Pass')
        self.assertEqual(self.result.sgpa, Decimal('10.00'))
        self.assertEqual(self.result.cgpa, Decimal('10.00'))

    def test_result_list_view(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('result_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Circuit Analysis')

    def test_result_pdf_download_for_student(self):
        self.client.login(username='2026EE001', password='testpassword123')
        response = self.client.get(reverse('student_result_pdf', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 1000)

    def test_student_export_excel(self):
        self.client.login(username='admin_test', password='testpassword123')
        response = self.client.get(reverse('student_export_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertTrue(len(response.content) > 1000)

