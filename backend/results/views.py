from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template.loader import get_template
from django.db.models import Q
from decimal import Decimal
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from xhtml2pdf import pisa

# Auth decorators
from accounts.decorators import admin_required, student_required

# App models
from students.models import Student
from results.models import SemesterResult

@login_required
@admin_required
def result_list(request):
    query = request.GET.get('q', '')
    sem = request.GET.get('semester', '')
    
    results = SemesterResult.objects.select_related('student__department').all().order_by('-id')
    
    if query:
        results = results.filter(
            Q(student__name__icontains=query) |
            Q(student__roll_number__icontains=query) |
            Q(subject_code__icontains=query) |
            Q(subject_name__icontains=query)
        )
    if sem:
        results = results.filter(semester=sem)
        
    paginator = Paginator(results, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'sem': int(sem) if sem.isdigit() else '',
        'semester_choices': range(1, 9)
    }
    return render(request, 'results/list.html', context)

@login_required
@admin_required
def result_add(request):
    students = Student.objects.all().order_by('name')
    if request.method == 'POST':
        student_id = request.POST.get('student')
        semester = request.POST.get('semester')
        subject_name = request.POST.get('subject_name')
        subject_code = request.POST.get('subject_code')
        internal_marks = request.POST.get('internal_marks')
        external_marks = request.POST.get('external_marks')
        credit = request.POST.get('credit')
        
        # Validations
        if not all([student_id, semester, subject_name, subject_code, internal_marks, external_marks, credit]):
            messages.error(request, "All fields are required.")
        else:
            try:
                student = get_object_or_404(Student, pk=student_id)
                # Check for duplicates (same student, same semester, same subject)
                if SemesterResult.objects.filter(student=student, semester=semester, subject_code=subject_code).exists():
                    messages.error(request, f"Result for {subject_code} in Semester {semester} already exists for this student.")
                else:
                    res = SemesterResult(
                        student=student,
                        semester=int(semester),
                        subject_name=subject_name,
                        subject_code=subject_code,
                        internal_marks=Decimal(internal_marks),
                        external_marks=Decimal(external_marks),
                        credit=int(credit)
                    )
                    res.save()
                    messages.success(request, f"Result for '{subject_name}' published successfully!")
                    return redirect('result_list')
            except Exception as e:
                messages.error(request, f"Error saving result. Details: {str(e)}")
                
    context = {
        'title': 'Add Semester Result',
        'students': students,
        'semester_choices': range(1, 9)
    }
    return render(request, 'results/form.html', context)

@login_required
@admin_required
def result_edit(request, pk):
    result = get_object_or_404(SemesterResult, pk=pk)
    students = Student.objects.all().order_by('name')
    
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        internal_marks = request.POST.get('internal_marks')
        external_marks = request.POST.get('external_marks')
        credit = request.POST.get('credit')
        
        if not all([subject_name, internal_marks, external_marks, credit]):
            messages.error(request, "All fields are required.")
        else:
            try:
                result.subject_name = subject_name
                result.internal_marks = Decimal(internal_marks)
                result.external_marks = Decimal(external_marks)
                result.credit = int(credit)
                result.save() # recalculation runs on save()
                messages.success(request, f"Result for '{subject_name}' updated successfully!")
                return redirect('result_list')
            except Exception as e:
                messages.error(request, f"Error updating result. Details: {str(e)}")
                
    context = {
        'title': 'Edit Semester Result',
        'result': result,
        'students': students,
        'semester_choices': range(1, 9)
    }
    return render(request, 'results/form.html', context)

@login_required
@admin_required
def result_delete(request, pk):
    result = get_object_or_404(SemesterResult, pk=pk)
    student = result.student
    result.delete()
    
    # Recalculate CGPA after deleting a result
    # We fetch a remaining result to trigger recalc or do bulk calculation
    remaining_results = SemesterResult.objects.filter(student=student)
    if remaining_results.exists():
        first_rem = remaining_results.first()
        first_rem.recalculate_gpas()
    else:
        pass
        
    messages.success(request, "Result record deleted successfully!")
    return redirect('result_list')

@login_required
@student_required
def student_result_view(request):
    student = request.user.student_profile
    all_results = SemesterResult.objects.filter(student=student).order_by('semester', 'subject_code')
    
    # Group results by semester
    grouped_results = {}
    for r in all_results:
        if r.semester not in grouped_results:
            grouped_results[r.semester] = {
                'results': [],
                'sgpa': r.sgpa,
                'cgpa': r.cgpa,
            }
        grouped_results[r.semester]['results'].append(r)
        
    context = {
        'student': student,
        'grouped_results': grouped_results,
    }
    return render(request, 'results/student_results.html', context)

@login_required
@student_required
def student_result_pdf(request, semester_num):
    student = request.user.student_profile
    results = SemesterResult.objects.filter(student=student, semester=semester_num).order_by('subject_code')
    
    if not results.exists():
        return HttpResponse("No result found for this semester.", status=404)
        
    sgpa = results.first().sgpa
    cgpa = results.first().cgpa
    
    context = {
        'student': student,
        'semester': semester_num,
        'results': results,
        'sgpa': sgpa,
        'cgpa': cgpa,
        'today': Decimal('0.00'), # Will be formatted in template
    }
    
    # Render PDF using xhtml2pdf
    template = get_template('results/pdf_gradesheet.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="GradeSheet_Sem{semester_num}_{student.roll_number}.pdf"'
        return response
    return HttpResponse("Error generating PDF", status=500)

@login_required
@admin_required
def student_export_excel(request):
    # Create workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Students List"
    
    # Set headers
    headers = [
        "Student ID", "Roll Number", "Registration Number", 
        "Name", "Email", "Phone", "Gender", "Date of Birth", 
        "Address", "Department", "Course", "Current Semester", 
        "Academic Year", "Admission Date"
    ]
    
    # Header styling
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    
    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    # Get students
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
            s.department.name,
            s.course.name,
            f"Semester {s.semester}",
            s.academic_year,
            s.admission_date.strftime('%Y-%m-%d') if s.admission_date else ''
        ]
        ws.append(row)
        
    # Adjust column widths automatically
    for col in ws.columns:
        max_len = 0
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value or '')
            if len(val) > max_len:
                max_len = len(val)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 10)
        
    # Set up response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=students_directory.xlsx"
    
    # Save workbook to memory and return
    wb.save(response)
    return response
