
# Create your views here.
from django.shortcuts import render
from .models import Beneficiary

def home_view(request):
    """Renderiza la plantilla base para comprobar la estructura de navegación"""
    return render(request, 'base.html')

def attendance_view(request):
    # 1. Traemos a todos los beneficiarios de la base de datos
    # En el futuro filtraremos por el grupo seleccionado (ej. Primaria)
    students = Beneficiary.objects.all()
    
    # 2. Pasamos los datos al HTML mediante el "contexto" (el diccionario final)
    return render(request, 'attendance.html', {'students': students})