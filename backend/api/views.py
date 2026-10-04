from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from decimal import Decimal
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from xhtml2pdf import pisa
from django.template.loader import get_template

from accounts.models import User, AdminProfile
from departments.models import Department
from courses.models import Course
from students.models import Student
from results.models import SemesterResult

from .serializers import (
    UserSerializer, AdminProfileSerializer,
    DepartmentSerializer, CourseSerializer,
    StudentSerializer, SemesterResultSerializer
)

# ================= AUTHENTICATION APIS =================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials. Please check your username and password.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    
    # Retrieve display name
    name = user.get_full_name() or user.username
    student_id = None
    if user.is_student and hasattr(user, 'student_profile'):
        name = user.student_profile.name
        student_id = user.student_profile.id
    elif user.is_admin and hasattr(user, 'admin_profile'):
        name = user.admin_profile.name

    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'name': name,
            'student_id': student_id
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logged out successfully.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'name': user.get_full_name() or user.username,
    }
    if user.is_student and hasattr(user, 'student_profile'):
        data['student'] = StudentSerializer(user.student_profile).data
        data['name'] = user.student_profile.name
    elif user.is_admin and hasattr(user, 'admin_profile'):
        data['admin_profile'] = AdminProfileSerializer(user.admin_profile).data
        data['name'] = user.admin_profile.name

    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    data = request.data
    student_id = data.get('student_id')
    name = data.get('name')
    roll_number = data.get('roll_number')
    registration_number = data.get('registration_number')
    email = data.get('email')
    phone = data.get('phone', '')
    gender = data.get('gender', 'Other')
    dob = data.get('dob')
    address = data.get('address', '')
    department_id = data.get('department')
    course_id = data.get('course')
    semester = data.get('semester', 1)
    academic_year = data.get('academic_year', '2026-2030')
    admission_date = data.get('admission_date')
    password = data.get('password')

    if not all([student_id, name, roll_number, registration_number, email, department_id, course_id, password]):
        return Response({'error': 'Please fill in all required fields.'}, status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        return Response({'error': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

    if Student.objects.filter(student_id=student_id).exists():
        return Response({'error': 'Student ID already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    if Student.objects.filter(roll_number=roll_number).exists() or User.objects.filter(username=roll_number).exists():
        return Response({'error': 'Roll Number (Username) already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    if Student.objects.filter(registration_number=registration_number).exists():
        return Response({'error': 'Registration Number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists() or Student.objects.filter(email=email).exists():
        return Response({'error': 'Email address is already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=roll_number,
                email=email,
                password=password,
                first_name=name.split()[0] if name.split() else name,
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                role='student'
            )
            student = Student.objects.create(
                student_id=student_id,
                user=user,
                roll_number=roll_number,
                registration_number=registration_number,
                name=name,
                email=email,
                phone=phone,
                gender=gender,
                dob=dob,
                address=address,
                department_id=department_id,
                course_id=course_id,
                semester=int(semester),
                academic_year=academic_year,
                admission_date=admission_date
            )
            token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'message': 'Account created successfully!',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'name': student.name,
                'student_id': student.id
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': f'Registration failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

# ================= DASHBOARD METRICS APIS =================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_admin_dashboard(request):
    if not request.user.is_admin:
        return Response({'error': 'Forbidden: Admin access only.'}, status=status.HTTP_403_FORBIDDEN)

    total_students = Student.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    total_results = SemesterResult.objects.count()

    recent_students = Student.objects.select_related('department', 'course').order_by('-id')[:5]

    depts = Department.objects.annotate(student_count=Count('students'))
    dept_distribution = [
        {'name': d.name, 'code': d.code, 'count': d.student_count}
        for d in depts
    ]

    return Response({
        'total_students': total_students,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_results': total_results,
        'dept_distribution': dept_distribution,
        'recent_students': StudentSerializer(recent_students, many=True).data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_student_dashboard(request):
    if not request.user.is_student or not hasattr(request.user, 'student_profile'):
        return Response({'error': 'Forbidden: Student profile not found.'}, status=status.HTTP_403_FORBIDDEN)

    student = request.user.student_profile
    all_results = SemesterResult.objects.filter(student=student).order_by('-semester')

    latest_sem = None
    latest_results_list = []
    if all_results.exists():
        latest_sem = all_results.first().semester
        latest_results_list = all_results.filter(semester=latest_sem)

    overall_cgpa = all_results.first().cgpa if all_results.exists() else Decimal('0.00')
    total_passed = all_results.filter(result_status='Pass').count()
    total_failed = all_results.filter(result_status='Fail').count()

    return Response({
        'student': StudentSerializer(student).data,
        'latest_semester': latest_sem,
        'overall_cgpa': str(overall_cgpa),
        'total_passed': total_passed,
        'total_failed': total_failed,
        'attendance_percentage': 88.5,
        'latest_results': SemesterResultSerializer(latest_results_list, many=True).data
    })

# ================= CRUD VIEWSETS =================

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('code')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Allow any authenticated user (e.g. registration dropdowns) to read, admin to write
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('code')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('department', 'course').all().order_by('-id')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.query_params.get('q', '')
        dept_id = self.request.query_params.get('department')
        sem = self.request.query_params.get('semester')

        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(roll_number__icontains=query) |
                Q(registration_number__icontains=query)
            )
        if dept_id and dept_id.isdigit():
            qs = qs.filter(department_id=dept_id)
        if sem and sem.isdigit():
            qs = qs.filter(semester=sem)
        return qs

    def perform_destroy(self, instance):
        with transaction.atomic():
            user = instance.user
            instance.delete()
            if user:
                user.delete()

class SemesterResultViewSet(viewsets.ModelViewSet):
    queryset = SemesterResult.objects.select_related('student__department').all().order_by('-id')
    serializer_class = SemesterResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.query_params.get('q', '')
        sem = self.request.query_params.get('semester')
        student_id = self.request.query_params.get('student')

        if student_id:
            qs = qs.filter(student_id=student_id)
        if query:
            qs = qs.filter(
                Q(student__name__icontains=query) |
                Q(student__roll_number__icontains=query) |
                Q(subject_code__icontains=query) |
                Q(subject_name__icontains=query)
            )
        if sem and sem.isdigit():
            qs = qs.filter(semester=sem)
        return qs

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_results(request):
    if not request.user.is_student or not hasattr(request.user, 'student_profile'):
        return Response({'error': 'Student profile not found.'}, status=status.HTTP_403_FORBIDDEN)

    student = request.user.student_profile
    all_results = SemesterResult.objects.filter(student=student).order_by('semester', 'subject_code')

    grouped = {}
    for r in all_results:
        if r.semester not in grouped:
            grouped[r.semester] = {
                'semester': r.semester,
                'sgpa': str(r.sgpa or '0.00'),
                'cgpa': str(r.cgpa or '0.00'),
                'results': []
            }
        grouped[r.semester]['results'].append(SemesterResultSerializer(r).data)

    return Response({
        'student': StudentSerializer(student).data,
        'grouped_results': list(grouped.values())
    })

# ================= EXPORT APIS =================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_export_excel(request):
    if not request.user.is_admin:
        return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students List"

    headers = [
        "Student ID", "Roll Number", "Registration Number", 
        "Name", "Email", "Phone", "Gender", "Date of Birth", 
        "Address", "Department", "Course", "Current Semester", 
        "Academic Year", "Admission Date"
    ]

    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    students = Student.objects.select_related('department', 'course').all().order_by('roll_number')
    for s in students:
        row = [
            s.student_id,
            s.roll_number,
            s.registration_number,
            s.name,
            s.email,
            s.phone,
            s.gender,
            s.dob.strftime('%Y-%m-%d') if s.dob else '',
            s.address,
            s.department.name if s.department else '',
            s.course.name if s.course else '',
            f"Semester {s.semester}",
            s.academic_year,
            s.admission_date.strftime('%Y-%m-%d') if s.admission_date else ''
        ]
        ws.append(row)

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 10)

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=students_directory.xlsx"
    wb.save(response)
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_download_pdf(request, semester_num):
    # Available for student themselves or admin
    student_id = request.query_params.get('student_id')
    if request.user.is_admin and student_id:
        student = Student.objects.filter(pk=student_id).first()
    elif request.user.is_student and hasattr(request.user, 'student_profile'):
        student = request.user.student_profile
    else:
        return Response({'error': 'Unauthorized or student profile missing.'}, status=status.HTTP_403_FORBIDDEN)

    if not student:
        return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

    results = SemesterResult.objects.filter(student=student, semester=semester_num).order_by('subject_code')
    if not results.exists():
        return Response({'error': 'No results found for this semester.'}, status=status.HTTP_404_NOT_FOUND)

    context = {
        'student': student,
        'semester': semester_num,
        'results': results,
        'sgpa': results.first().sgpa,
        'cgpa': results.first().cgpa,
    }

    template = get_template('results/pdf_gradesheet.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="GradeSheet_Sem{semester_num}_{student.roll_number}.pdf"'
        return response
    return Response({'error': 'Error generating PDF.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
