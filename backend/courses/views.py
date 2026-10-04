from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required
from .models import Course

@login_required
@admin_required
def course_list(request):
    courses = Course.objects.all().order_by('code')
    return render(request, 'courses/list.html', {'courses': courses})

@login_required
@admin_required
def course_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        duration = request.POST.get('duration')
        description = request.POST.get('description')
        
        if not name or not code or not duration:
            messages.error(request, "Name, Code, and Duration are required fields.")
        elif Course.objects.filter(code=code).exists():
            messages.error(request, "A course with this code already exists.")
        else:
            Course.objects.create(name=name, code=code, duration=duration, description=description)
            messages.success(request, f"Course '{name}' added successfully!")
            return redirect('course_list')
            
    return render(request, 'courses/form.html', {'title': 'Add Course'})

@login_required
@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        duration = request.POST.get('duration')
        description = request.POST.get('description')
        
        if not name or not code or not duration:
            messages.error(request, "Name, Code, and Duration are required fields.")
        elif Course.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, "A course with this code already exists.")
        else:
            course.name = name
            course.code = code
            course.duration = duration
            course.description = description
            course.save()
            messages.success(request, f"Course '{name}' updated successfully!")
            return redirect('course_list')
            
    return render(request, 'courses/form.html', {'title': 'Edit Course', 'course': course})

@login_required
@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # Check if there are students in this course
    if course.students.exists():
        messages.error(request, f"Cannot delete course '{course.name}' because it contains students.")
    else:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    return redirect('course_list')
