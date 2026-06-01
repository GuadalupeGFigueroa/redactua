# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('api/group/<int:group_id>/students/',views.get_students_by_group, name='api_group_students'),
    path('api/attendance/update/', views.update_attendance, name='api_update_attendance'),
    path('expedientes/', views.family_case_list, name='family_case_list'),
    path('expedientes/nuevo/', views.family_case_create, name='family_case_create'),
    path('expedientes/<int:case_id>/', views.family_case_detail, name='family_case_detail'),
    path('expedientes/<int:case_id>/nuevo-miembro/', views.beneficiary_create, name='beneficiary_create'),
    path('estadisticas/', views.statistics_view, name='statistics'),
]
