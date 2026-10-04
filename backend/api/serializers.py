from rest_framework import serializers
from accounts.models import User, AdminProfile
from departments.models import Department
from courses.models import Course
from students.models import Student
from results.models import SemesterResult
from decimal import Decimal

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']

class AdminProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AdminProfile
        fields = ['id', 'user', 'employee_id', 'name', 'phone', 'designation', 'profile_photo']

class DepartmentSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'student_count']

    def get_student_count(self, obj):
        return obj.students.count()

class CourseSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'duration', 'description', 'student_count']

    def get_student_count(self, obj):
        return obj.students.count()

class StudentSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    department_code = serializers.CharField(source='department.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'roll_number', 'registration_number', 'name',
            'email', 'phone', 'gender', 'dob', 'address',
            'department', 'department_name', 'department_code',
            'course', 'course_name', 'course_code',
            'semester', 'academic_year', 'admission_date', 'profile_photo'
        ]

class SemesterResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_roll = serializers.CharField(source='student.roll_number', read_only=True)

    class Meta:
        model = SemesterResult
        fields = [
            'id', 'student', 'student_name', 'student_roll',
            'semester', 'subject_name', 'subject_code',
            'internal_marks', 'external_marks', 'total',
            'grade', 'credit', 'sgpa', 'cgpa', 'result_status'
        ]
        read_only_fields = ['total', 'grade', 'sgpa', 'cgpa', 'result_status']
