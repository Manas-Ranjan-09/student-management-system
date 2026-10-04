from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    api_login, api_logout, api_me, api_register,
    api_admin_dashboard, api_student_dashboard,
    DepartmentViewSet, CourseViewSet, StudentViewSet, SemesterResultViewSet,
    api_my_results, api_export_excel, api_download_pdf
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='api_department')
router.register(r'courses', CourseViewSet, basename='api_course')
router.register(r'students', StudentViewSet, basename='api_student')
router.register(r'results', SemesterResultViewSet, basename='api_result')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', api_login, name='api_login'),
    path('auth/logout/', api_logout, name='api_logout'),
    path('auth/me/', api_me, name='api_me'),
    path('auth/register/', api_register, name='api_register'),

    # Dashboards
    path('dashboard/admin/', api_admin_dashboard, name='api_admin_dashboard'),
    path('dashboard/student/', api_student_dashboard, name='api_student_dashboard'),

    # Student personal results
    path('results/my-results/', api_my_results, name='api_my_results'),
    path('results/download-pdf/<int:semester_num>/', api_download_pdf, name='api_download_pdf'),

    # Exports
    path('students/export-excel/', api_export_excel, name='api_export_excel'),

    # CRUD Router
    path('', include(router.urls)),
]
