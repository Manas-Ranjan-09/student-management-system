"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Import app views
from accounts.views import (
    login_view, logout_view, change_password_view, 
    dashboard_redirect, admin_dashboard, student_dashboard, register_view,
    admin_profile_view
)
from departments.views import (
    department_list, department_add, department_edit, department_delete,
    department_detail
)
from courses.views import (
    course_list, course_add, course_edit, course_delete
)
from students.views import (
    student_list, student_detail, student_add, student_edit, student_delete
)
from results.views import (
    result_list, result_add, result_edit, result_delete,
    student_result_view, student_result_pdf, student_export_excel
)

urlpatterns = [
    path('django-admin/', admin.site.urls),
    
    # Authentication & Session Redirects
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('change-password/', change_password_view, name='change_password'),
    path('dashboard/redirect/', dashboard_redirect, name='dashboard_redirect'),
    
    # Dashboards
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/profile/', admin_profile_view, name='admin_profile'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
    
    # Department Module (Admin CRUD)
    path('departments/', department_list, name='department_list'),
    path('departments/add/', department_add, name='department_add'),
    path('departments/edit/<int:pk>/', department_edit, name='department_edit'),
    path('departments/delete/<int:pk>/', department_delete, name='department_delete'),
    path('departments/view/<int:pk>/', department_detail, name='department_detail'),
    
    # Course Module (Admin CRUD)
    path('courses/', course_list, name='course_list'),
    path('courses/add/', course_add, name='course_add'),
    path('courses/edit/<int:pk>/', course_edit, name='course_edit'),
    path('courses/delete/<int:pk>/', course_delete, name='course_delete'),
    
    # Student Module (Admin CRUD + Details)
    path('students/', student_list, name='student_list'),
    path('students/add/', student_add, name='student_add'),
    path('students/edit/<int:pk>/', student_edit, name='student_edit'),
    path('students/delete/<int:pk>/', student_delete, name='student_delete'),
    path('students/view/<int:pk>/', student_detail, name='student_detail'),
    path('students/export-excel/', student_export_excel, name='student_export_excel'),
    
    # Semester Result Module (Admin CRUD + Student views + PDF Exporter)
    path('results/', result_list, name='result_list'),
    path('results/add/', result_add, name='result_add'),
    path('results/edit/<int:pk>/', result_edit, name='result_edit'),
    path('results/delete/<int:pk>/', result_delete, name='result_delete'),
    path('results/student/', student_result_view, name='student_result_view'),
    path('results/student/download-pdf/<int:semester_num>/', student_result_pdf, name='student_result_pdf'),
]

# Serve uploaded media files reliably across both development and production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

handler404 = 'accounts.views.error_404_view'
handler500 = 'accounts.views.error_500_view'


