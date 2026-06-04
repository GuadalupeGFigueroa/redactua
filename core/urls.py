# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Ruta a inicio
    path('', views.home_view, name='home'),
    
    # Rutas para usuarios (Beneficiarios)
    path('usuarios/', views.beneficiary_list, name='beneficiary_list'),
    path('usuarios/<int:pk>/', views.beneficiary_detail, name='beneficiary_detail'),
    path('usuarios/<int:pk>/editar/', views.beneficiary_update, name='beneficiary_update'),
    path('usuarios/<int:pk>/eliminar/', views.beneficiary_delete, name='beneficiary_delete'),

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

    # Ruta para actividades
    path('actividades/', views.group_list, name='group_list'),

    # Rutas para asistencia 
    path('asistencia/', views.attendance_view, name='attendance'),

    # Rutas para estadísticas
    path('estadisticas/', views.statistics_view, name='statistics'),

    # --- RUTAS DE API INTERNA ---
    path('api/group/<int:group_id>/students/', views.get_students_by_group, name='api_group_students'),
    path('api/attendance/update/', views.update_attendance, name='api_update_attendance'),

    # Ruta para el cierre de sesión nativo de Django
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]