from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from datetime import date

# Import models
from accounts.models import User, AdminProfile
from departments.models import Department
from courses.models import Course
from students.models import Student
from results.models import SemesterResult

class Command(BaseCommand):
    help = 'Seeds the database with initial sample data (Admin, Departments, Courses, Students, Results)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Starting database seeding...'))

        try:
            with transaction.atomic():
                # 1. Create Admin User
                if not User.objects.filter(username='admin').exists():
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email='admin@sms.com',
                        password='adminpassword',
                        first_name='System',
                        last_name='Administrator'
                    )
                    AdminProfile.objects.create(
                        user=admin_user,
                        employee_id='EMP2026001',
                        name='System Administrator',
                        phone='+15550100',
                        designation='Chief IT Administrator'
                    )
                    self.stdout.write(self.style.SUCCESS('Admin user and profile created successfully! (Username: admin, Password: adminpassword)'))
                else:
                    admin_user = User.objects.get(username='admin')
                    AdminProfile.objects.get_or_create(
                        user=admin_user,
                        defaults={
                            'employee_id': 'EMP2026001',
                            'name': 'System Administrator',
                            'phone': '+15550100',
                            'designation': 'Chief IT Administrator'
                        }
                    )
                    self.stdout.write('Admin user already exists. Verified admin profile existence.')

                # 2. Create Departments
                cse, _ = Department.objects.get_or_create(
                    code='CSE',
                    defaults={'name': 'Computer Science & Engineering', 'description': 'Department of Computer Science and software related studies.'}
                )
                eee, _ = Department.objects.get_or_create(
                    code='EEE',
                    defaults={'name': 'Electrical & Electronics Engineering', 'description': 'Department of Power, Electronics, and circuits.'}
                )
                me, _ = Department.objects.get_or_create(
                    code='ME',
                    defaults={'name': 'Mechanical Engineering', 'description': 'Department of Machine dynamics, Design, and Thermodynamics.'}
                )
                self.stdout.write(self.style.SUCCESS('Departments seeded.'))

                # 3. Create Courses
                btech_cse, _ = Course.objects.get_or_create(
                    code='BTECH-CS',
                    defaults={'name': 'B.Tech in Computer Science', 'duration': '4 Years', 'description': 'Bachelor of Technology in Computer Science & Engineering.'}
                )
                btech_eee, _ = Course.objects.get_or_create(
                    code='BTECH-EE',
                    defaults={'name': 'B.Tech in Electrical Engineering', 'duration': '4 Years', 'description': 'Bachelor of Technology in Electrical & Electronics Engineering.'}
                )
                mca, _ = Course.objects.get_or_create(
                    code='MCA',
                    defaults={'name': 'Master of Computer Applications', 'duration': '2 Years', 'description': 'Postgraduate degree in computer application development.'}
                )
                self.stdout.write(self.style.SUCCESS('Courses seeded.'))

                # 4. Create Students (linked User accounts are automatically created)
                student_data = [
                    {
                        'username': '2026CSE001',
                        'email': 'jane@student.com',
                        'name': 'Jane Doe',
                        'student_id': 'STU2026001',
                        'roll_number': '2026CSE001',
                        'registration_number': 'REG2026CSE001',
                        'phone': '+15550101',
                        'gender': 'Female',
                        'dob': date(2004, 5, 15),
                        'address': '123 Academic Way, Boston, MA',
                        'department': cse,
                        'course': btech_cse,
                        'semester': 5,
                        'academic_year': '2024-2028',
                        'admission_date': date(2024, 8, 1)
                    },
                    {
                        'username': '2026EEE002',
                        'email': 'john@student.com',
                        'name': 'John Smith',
                        'student_id': 'STU2026002',
                        'roll_number': '2026EEE002',
                        'registration_number': 'REG2026EEE002',
                        'phone': '+15550102',
                        'gender': 'Male',
                        'dob': date(2003, 8, 22),
                        'address': '456 Volt Circuit, Austin, TX',
                        'department': eee,
                        'course': btech_eee,
                        'semester': 5,
                        'academic_year': '2024-2028',
                        'admission_date': date(2024, 8, 1)
                    },
                    {
                        'username': '2026MCA003',
                        'email': 'alice@student.com',
                        'name': 'Alice Cooper',
                        'student_id': 'STU2026003',
                        'roll_number': '2026MCA003',
                        'registration_number': 'REG2026MCA003',
                        'phone': '+15550103',
                        'gender': 'Female',
                        'dob': date(2001, 11, 3),
                        'address': '789 Algorithm Lane, Seattle, WA',
                        'department': cse,
                        'course': mca,
                        'semester': 3,
                        'academic_year': '2025-2027',
                        'admission_date': date(2025, 8, 1)
                    }
                ]

                students = []
                for s_info in student_data:
                    if not User.objects.filter(username=s_info['username']).exists():
                        # Create User login
                        user = User.objects.create_user(
                            username=s_info['username'],
                            email=s_info['email'],
                            password='studentpassword', # default password for students
                            first_name=s_info['name'].split()[0],
                            last_name=s_info['name'].split()[1] if len(s_info['name'].split()) > 1 else '',
                            role='student'
                        )
                        # Create Profile
                        student = Student.objects.create(
                            student_id=s_info['student_id'],
                            user=user,
                            roll_number=s_info['roll_number'],
                            registration_number=s_info['registration_number'],
                            name=s_info['name'],
                            email=s_info['email'],
                            phone=s_info['phone'],
                            gender=s_info['gender'],
                            dob=s_info['dob'],
                            address=s_info['address'],
                            department=s_info['department'],
                            course=s_info['course'],
                            semester=s_info['semester'],
                            academic_year=s_info['academic_year'],
                            admission_date=s_info['admission_date']
                        )
                        students.append(student)
                        self.stdout.write(self.style.SUCCESS(f"Student seeded: {s_info['name']} (Username: {s_info['username']}, Password: studentpassword)"))
                    else:
                        students.append(Student.objects.get(roll_number=s_info['username']))

                # 5. Create Results for Jane Doe (Semester 5)
                jane = students[0]
                results_data = [
                    {'subject_name': 'Computer Networks', 'subject_code': 'CS-501', 'credit': 4, 'internal': Decimal('27.00'), 'external': Decimal('58.00'), 'semester': 5},
                    {'subject_name': 'Database Management Systems', 'subject_code': 'CS-502', 'credit': 4, 'internal': Decimal('29.00'), 'external': Decimal('62.00'), 'semester': 5},
                    {'subject_name': 'Software Engineering', 'subject_code': 'CS-503', 'credit': 3, 'internal': Decimal('24.00'), 'external': Decimal('51.00'), 'semester': 5},
                    {'subject_name': 'Theory of Computation', 'subject_code': 'CS-504', 'credit': 4, 'internal': Decimal('21.00'), 'external': Decimal('42.00'), 'semester': 5},
                    # Add Semester 4 results to test CGPA calculation
                    {'subject_name': 'Operating Systems', 'subject_code': 'CS-401', 'credit': 4, 'internal': Decimal('25.00'), 'external': Decimal('53.00'), 'semester': 4},
                    {'subject_name': 'Design & Analysis of Algorithms', 'subject_code': 'CS-402', 'credit': 4, 'internal': Decimal('28.00'), 'external': Decimal('59.00'), 'semester': 4},
                ]

                for r_info in results_data:
                    # Check if result already exists
                    if not SemesterResult.objects.filter(student=jane, semester=r_info['semester'], subject_code=r_info['subject_code']).exists():
                        res = SemesterResult(
                            student=jane,
                            semester=r_info['semester'],
                            subject_name=r_info['subject_name'],
                            subject_code=r_info['subject_code'],
                            credit=r_info['credit'],
                            internal_marks=r_info['internal'],
                            external_marks=r_info['external']
                        )
                        res.save()
                        self.stdout.write(f"Result published for Jane Doe: {r_info['subject_name']} (Sem {r_info['semester']})")

                self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding database: {str(e)}'))
