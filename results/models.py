from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from students.models import Student

class SemesterResult(models.Model):
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]
    
    STATUS_CHOICES = (
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    )

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20)
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., out of 30 or 40
    external_marks = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., out of 70 or 60
    total = models.DecimalField(max_digits=5, decimal_places=2, blank=True)
    grade = models.CharField(max_length=2, blank=True)
    credit = models.IntegerField(default=3)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    result_status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True)

    class Meta:
        unique_together = ('student', 'semester', 'subject_code')

    def clean(self):
        # Validation checks
        if self.internal_marks < 0 or self.external_marks < 0:
            raise ValidationError("Marks cannot be negative.")
        if self.internal_marks > 100 or self.external_marks > 100:
            raise ValidationError("Individual marks component cannot exceed 100.")
        if (self.internal_marks + self.external_marks) > 100:
            raise ValidationError("Total marks (Internal + External) cannot exceed 100.")

    def save(self, *args, **kwargs):
        self.clean()
        
        # 1. Calculate Total Marks
        self.total = self.internal_marks + self.external_marks
        
        # 2. Calculate Grade and Status
        if self.total >= Decimal('90.00'):
            self.grade = 'A+'
        elif self.total >= Decimal('80.00'):
            self.grade = 'A'
        elif self.total >= Decimal('70.00'):
            self.grade = 'B'
        elif self.total >= Decimal('60.00'):
            self.grade = 'C'
        elif self.total >= Decimal('50.00'):
            self.grade = 'D'
        elif self.total >= Decimal('40.00'):
            self.grade = 'E'
        else:
            self.grade = 'F'
            
        self.result_status = 'Pass' if self.total >= Decimal('40.00') else 'Fail'
        
        # Save first so database contains this record before recalculating SGPA/CGPA
        super(SemesterResult, self).save(*args, **kwargs)
        
        # Recalculate SGPA and CGPA for this student
        self.recalculate_gpas()

    def recalculate_gpas(self):
        # We fetch all results for this student
        all_results = SemesterResult.objects.filter(student=self.student)
        
        # Map grade to grade points
        grade_points_map = {
            'A+': 10,
            'A': 9,
            'B': 8,
            'C': 7,
            'D': 6,
            'E': 5,
            'F': 0
        }
        
        # Group results by semester to compute SGPA per semester
        semesters_present = all_results.values_list('semester', flat=True).distinct()
        
        # Calculate SGPA for each semester and update them
        for sem in semesters_present:
            sem_results = all_results.filter(semester=sem)
            total_sem_credits = 0
            weighted_sem_points = 0
            for r in sem_results:
                points = grade_points_map.get(r.grade, 0)
                weighted_sem_points += points * r.credit
                total_sem_credits += r.credit
                
            sem_sgpa = Decimal('0.00')
            if total_sem_credits > 0:
                sem_sgpa = Decimal(weighted_sem_points) / Decimal(total_sem_credits)
                
            # Perform bulk update without calling save() recursively to avoid infinite loop
            SemesterResult.objects.filter(student=self.student, semester=sem).update(sgpa=round(sem_sgpa, 2))
            if sem == self.semester:
                self.sgpa = round(sem_sgpa, 2)

        # Calculate Overall CGPA (weighted sum of all semesters)
        total_credits = 0
        weighted_points = 0
        for r in all_results:
            points = grade_points_map.get(r.grade, 0)
            weighted_points += points * r.credit
            total_credits += r.credit
            
        overall_cgpa = Decimal('0.00')
        if total_credits > 0:
            overall_cgpa = Decimal(weighted_points) / Decimal(total_credits)
            
        # Update CGPA for all records of this student
        SemesterResult.objects.filter(student=self.student).update(cgpa=round(overall_cgpa, 2))
        self.cgpa = round(overall_cgpa, 2)

    def __str__(self):
        return f"{self.student.name} - Sem {self.semester} - {self.subject_name}"
