# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Ruta a inicio
    path('', views.home_view, name='home'),
    
    # Rutas para usuarios (Beneficiarios)
    path('usuarios/', views.beneficiary_list, name='beneficiary_list'),
    path('usuarios/<int:pk>/', views.beneficiary_detail, name='beneficiary_detail'),

    # Rutas para expedientes familiares
    path('expedientes/', views.family_case_list, name='family_case_list'),
    path('expedientes/nuevo/', views.family_case_create, name='family_case_create'),
    path('expedientes/<int:case_id>/', views.family_case_detail, name='family_case_detail'),
    path('expedientes/<int:case_id>/nuevo-miembro/', views.beneficiary_create, name='beneficiary_create'),

    # Rutas para contactos (Profesionales Externos)
    path('contactos/', views.external_professional_list, name='external_professional_list'),
    path('contactos/<int:pk>/', views.external_professional_detail, name='external_professional_detail'),

    # Rutas para trabajadores (Equipo)
    path('equipo/', views.worker_list, name='worker_list'),
    path('equipo/<int:pk>/', views.worker_detail, name='worker_detail'),

    # Rutas para asistencia 
    path('asistencia/', views.attendance_view, name='attendance'),

    # Rutas para estadísticas
    path('estadisticas/', views.statistics_view, name='statistics'),

    # --- RUTAS DE API INTERNA ---
    path('api/group/<int:group_id>/students/', views.get_students_by_group, name='api_group_students'),
    path('api/attendance/update/', views.update_attendance, name='api_update_attendance'),
]