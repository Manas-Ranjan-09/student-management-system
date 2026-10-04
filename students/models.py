from django.db import models
from django.conf import settings
from django.utils import timezone
from departments.models import Department
from courses.models import Course

class Student(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    student_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()
    address = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='students')
    semester = models.IntegerField(choices=SEMESTER_CHOICES, default=1)
    academic_year = models.CharField(max_length=9)  # e.g., "2025-2029"
    admission_date = models.DateField(default=timezone.now)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"
