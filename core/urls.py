# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('api/group/<int:group_id>/students/',views.get_students_by_group, name='api_group_students'),
    path('api/attendance/update/', views.update_attendance, name='api_update_attendance'),
]
