
from django.shortcuts import render
from .models import Group, Beneficiary

def home_view(request):
    """Renderiza la plantilla base para comprobar la estructura de navegación"""
    return render(request, 'base.html')

def attendance_view(request):
    """Muestra la pantalla de asistencia con los grupos y el alumnado correspondiente"""
    groups = Group.objects.all()
    if groups.exists():
        first_group = groups.first()
        students = first_group.beneficiaries.all()
    else:
        students = []
    
    context = {
        'groups': groups,
        'students': students,
    }
 
    
    # Pasamos los datos al HTML mediante el "contexto" (el diccionario final)
    return render(request, 'attendance.html', context)