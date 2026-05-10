
# Create your views here.
from django.shortcuts import render

def home_view(request):
    """Renderiza la plantilla base para comprobar la estructura de navegación"""
    return render(request, 'base.html')