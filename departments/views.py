from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required
from .models import Department

@login_required
@admin_required
def department_list(request):
    departments = Department.objects.all().order_by('code')
    return render(request, 'departments/list.html', {'departments': departments})

@login_required
@admin_required
def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        
        if not name or not code:
            messages.error(request, "Name and Code are required fields.")
        elif Department.objects.filter(code=code).exists():
            messages.error(request, "A department with this code already exists.")
        elif Department.objects.filter(name=name).exists():
            messages.error(request, "A department with this name already exists.")
        else:
            Department.objects.create(name=name, code=code, description=description)
            messages.success(request, f"Department '{name}' added successfully!")
            return redirect('department_list')
            
    return render(request, 'departments/form.html', {'title': 'Add Department'})

@login_required
@admin_required
def department_edit(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        
        if not name or not code:
            messages.error(request, "Name and Code are required fields.")
        elif Department.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, "A department with this code already exists.")
        elif Department.objects.filter(name=name).exclude(pk=pk).exists():
            messages.error(request, "A department with this name already exists.")
        else:
            dept.name = name
            dept.code = code
            dept.description = description
            dept.save()
            messages.success(request, f"Department '{name}' updated successfully!")
            return redirect('department_list')
            
    return render(request, 'departments/form.html', {'title': 'Edit Department', 'department': dept})

@login_required
@admin_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    # Check if there are students in this department to prevent accidental cascading problems
    if dept.students.exists():
        messages.error(request, f"Cannot delete department '{dept.name}' because it contains students.")
    else:
        dept.delete()
        messages.success(request, "Department deleted successfully!")
    return redirect('department_list')

@login_required
@admin_required
def department_detail(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    students = dept.students.select_related('course').all().order_by('roll_number')
    context = {
        'department': dept,
        'students': students
    }
    return render(request, 'departments/detail.html', context)
