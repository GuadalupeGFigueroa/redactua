# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('attendance/', views.attendance_view, name='attendance'),
]
