from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from decimal import Decimal
from datetime import date

# Import decorator helpers
from accounts.decorators import admin_required, student_required

# Import app models
from accounts.models import User, AdminProfile
from departments.models import Department
from courses.models import Course
from students.models import Student
from results.models import SemesterResult

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! Login successful.")
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        
        user = request.user
        if not user.check_password(old):
            messages.error(request, "Incorrect current password.")
        elif new != confirm:
            messages.error(request, "New passwords do not match.")
        elif len(new) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        else:
            user.set_password(new)
            user.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, "Your password was updated successfully!")
            return redirect('dashboard_redirect')
            
    return render(request, 'accounts/change_password.html')

@login_required
def dashboard_redirect(request):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    elif request.user.is_student:
        return redirect('student_dashboard')
    else:
        logout(request)
        messages.error(request, "Access Denied: Unknown role assignment.")
        return redirect('login')

@login_required
@admin_required
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    total_results = SemesterResult.objects.count()
    
    recent_students = Student.objects.select_related('department', 'course').order_by('-id')[:5]
    
    # Calculate chart data
    depts = Department.objects.annotate(student_count=Count('students'))
    dept_names = [dept.name for dept in depts]
    dept_student_counts = [dept.student_count for dept in depts]
    
    context = {
        'total_students': total_students,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_results': total_results,
        'recent_students': recent_students,
        'dept_names': dept_names,
        'dept_student_counts': dept_student_counts,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
@student_required
def student_dashboard(request):
    # Safe retrieval: check if student profile is configured
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        logout(request)
        messages.error(request, "Your student profile records were not found. Contact administration.")
        return redirect('login')
        
    # Get latest result records
    all_results = SemesterResult.objects.filter(student=student).order_by('-semester')
    
    latest_sem = None
    latest_results_list = []
    
    if all_results.exists():
        latest_sem = all_results.first().semester
        latest_results_list = all_results.filter(semester=latest_sem)
        
    overall_cgpa = all_results.first().cgpa if all_results.exists() else Decimal('0.00')
    
    # Calculate some progress metrics
    total_subjects_passed = all_results.filter(result_status='Pass').count()
    total_subjects_failed = all_results.filter(result_status='Fail').count()
    
    # Optional attendance percent mockup
    attendance_percentage = 88.5
    
    context = {
        'student': student,
        'latest_sem': latest_sem,
        'latest_results': latest_results_list,
        'overall_cgpa': overall_cgpa,
        'total_subjects_passed': total_subjects_passed,
        'total_subjects_failed': total_subjects_failed,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'dashboards/student_dashboard.html', context)

def error_404_view(request, exception):
    return render(request, '404.html', status=404)

def error_500_view(request):
    return render(request, '500.html', status=500)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
        
    departments = Department.objects.all().order_by('name')
    courses = Course.objects.all().order_by('name')
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        registration_number = request.POST.get('registration_number')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        address = request.POST.get('address')
        department_id = request.POST.get('department')
        course_id = request.POST.get('course')
        semester = request.POST.get('semester')
        academic_year = request.POST.get('academic_year')
        admission_date = request.POST.get('admission_date')
        profile_photo = request.FILES.get('profile_photo')
        
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validations
        if not all([student_id, name, roll_number, registration_number, email, department_id, course_id, password, confirm_password]):
            messages.error(request, "Please fill in all required fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
        elif Student.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists.")
        elif Student.objects.filter(roll_number=roll_number).exists() or User.objects.filter(username=roll_number).exists():
            messages.error(request, "Roll Number already exists.")
        elif Student.objects.filter(registration_number=registration_number).exists():
            messages.error(request, "Registration Number already exists.")
        elif Student.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Email address is already in use.")
        else:
            try:
                with transaction.atomic():
                    # Create User login
                    user = User.objects.create_user(
                        username=roll_number,
                        email=email,
                        password=password,
                        first_name=name.split()[0] if name.split() else name,
                        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                        role='student'
                    )
                    
                    # Create Profile
                    Student.objects.create(
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
                        admission_date=admission_date or date.today().strftime('%Y-%m-%d'),
                        profile_photo=profile_photo
                    )
                messages.success(request, "Account created successfully! You can now log in.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Registration failed. Error: {str(e)}")
                
    context = {
        'departments': departments,
        'courses': courses,
        'semester_choices': range(1, 9)
    }
    return render(request, 'accounts/register.html', context)

@login_required
@admin_required
def admin_profile_view(request):
    profile, created = AdminProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'employee_id': f"EMP{request.user.id:04d}",
            'name': request.user.get_full_name() or request.user.username,
            'designation': 'System Administrator'
        }
    )
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        designation = request.POST.get('designation')
        profile_photo = request.FILES.get('profile_photo')
        
        # Validation checks
        if not name or not email:
            messages.error(request, "Name and Email are required fields.")
        elif User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
            messages.error(request, "Email address is already in use by another account.")
        else:
            try:
                with transaction.atomic():
                    # Sync User changes
                    request.user.email = email
                    request.user.first_name = name.split()[0] if name.split() else name
                    request.user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                    request.user.save()
                    
                    # Save AdminProfile changes
                    profile.name = name
                    profile.phone = phone
                    profile.designation = designation
                    if profile_photo:
                        profile.profile_photo = profile_photo
                    profile.save()
                    
                messages.success(request, "Your administrator profile has been updated successfully!")
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f"Failed to save profile. Error: {str(e)}")
                
    return render(request, 'accounts/admin_profile.html', {'profile': profile})


