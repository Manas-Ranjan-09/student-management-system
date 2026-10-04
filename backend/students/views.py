from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from accounts.decorators import admin_required
from accounts.models import User
from departments.models import Department
from courses.models import Course
from .models import Student

@login_required
@admin_required
def student_list(request):
    query = request.GET.get('q', '')
    dept_id = request.GET.get('department', '')
    sem = request.GET.get('semester', '')
    
    students = Student.objects.select_related('department', 'course').all().order_by('-id')
    
    # Apply search query
    if query:
        students = students.filter(
            Q(name__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(registration_number__icontains=query)
        )
        
    # Apply filters
    if dept_id:
        students = students.filter(department_id=dept_id)
    if sem:
        students = students.filter(semester=sem)
        
    # Pagination: 10 students per page
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = Department.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'query': query,
        'dept_id': int(dept_id) if dept_id.isdigit() else '',
        'sem': int(sem) if sem.isdigit() else '',
        'semester_choices': range(1, 9)
    }
    return render(request, 'students/list.html', context)

@login_required
@admin_required
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related('department', 'course'), pk=pk)
    # Fetch results sorted by semester
    results = student.results.all().order_by('semester', 'subject_code')
    
    # Calculate unique semesters and CGPA
    cgpa = Decimal('0.00')
    if results.exists():
        cgpa = results.first().cgpa
        
    context = {
        'student': student,
        'results': results,
        'cgpa': cgpa
    }
    return render(request, 'students/detail.html', context)

@login_required
@admin_required
def student_add(request):
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
        
        # Passwords for student account
        password = request.POST.get('password')
        if not password:
            password = roll_number  # fallback to roll number
            
        # Field Validations
        if not all([student_id, name, roll_number, registration_number, email, department_id, course_id]):
            messages.error(request, "Please fill in all required fields.")
        elif Student.objects.filter(student_id=student_id).exists():
            messages.error(request, "Student ID already exists.")
        elif Student.objects.filter(roll_number=roll_number).exists() or User.objects.filter(username=roll_number).exists():
            messages.error(request, "Roll Number (which is also the login username) already exists.")
        elif Student.objects.filter(registration_number=registration_number).exists():
            messages.error(request, "Registration Number already exists.")
        elif Student.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Email address is already in use.")
        else:
            try:
                with transaction.atomic():
                    # Create the Django User account for logging in
                    user = User.objects.create_user(
                        username=roll_number,
                        email=email,
                        password=password,
                        first_name=name.split()[0] if name.split() else name,
                        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                        role='student'
                    )
                    
                    # Create the Student Profile linked to User
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
                        semester=semester,
                        academic_year=academic_year,
                        admission_date=admission_date,
                        profile_photo=profile_photo
                    )
                messages.success(request, f"Student '{name}' added and login account created successfully!")
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f"Failed to save student record. Error: {str(e)}")
                
    context = {
        'title': 'Add Student',
        'departments': departments,
        'courses': courses,
        'semester_choices': range(1, 9)
    }
    return render(request, 'students/form.html', context)

@login_required
@admin_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    departments = Department.objects.all().order_by('name')
    courses = Course.objects.all().order_by('name')
    
    if request.method == 'POST':
        name = request.POST.get('name')
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
        
        # Image photo upload check
        profile_photo = request.FILES.get('profile_photo')
        
        # Validations
        if not all([name, registration_number, email, department_id, course_id]):
            messages.error(request, "Please fill in all required fields.")
        elif Student.objects.filter(registration_number=registration_number).exclude(pk=pk).exists():
            messages.error(request, "Registration Number already exists.")
        elif Student.objects.filter(email=email).exclude(pk=pk).exists() or User.objects.filter(email=email).exclude(pk=student.user.pk).exists():
            messages.error(request, "Email address is already in use.")
        else:
            try:
                with transaction.atomic():
                    # Sync changes with User account
                    student.user.email = email
                    student.user.first_name = name.split()[0] if name.split() else name
                    student.user.last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                    student.user.save()
                    
                    # Save Student details
                    student.name = name
                    student.registration_number = registration_number
                    student.email = email
                    student.phone = phone
                    student.gender = gender
                    student.dob = dob
                    student.address = address
                    student.department_id = department_id
                    student.course_id = course_id
                    student.semester = semester
                    student.academic_year = academic_year
                    student.admission_date = admission_date
                    
                    if profile_photo:
                        student.profile_photo = profile_photo
                        
                    student.save()
                    
                messages.success(request, f"Student '{name}' details updated successfully!")
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f"Failed to update student. Error: {str(e)}")
                
    context = {
        'title': 'Edit Student',
        'student': student,
        'departments': departments,
        'courses': courses,
        'semester_choices': range(1, 9)
    }
    return render(request, 'students/form.html', context)

@login_required
@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    try:
        with transaction.atomic():
            # Deleting student cascades and deletes the linked User object due to user deletion
            student.user.delete()
        messages.success(request, "Student and corresponding login credentials deleted successfully!")
    except Exception as e:
        messages.error(request, f"Failed to delete student. Error: {str(e)}")
    return redirect('student_list')
