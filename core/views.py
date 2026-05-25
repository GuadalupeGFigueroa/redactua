
from django.shortcuts import render
from django.http import JsonResponse
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

def get_students_by_group(request, group_id):
    """API interna: DEvuelve los alumnos de un grupo específico en formato JSON"""
    try:
        group = Group.objects.get(id=group_id)
        # Obtenemos los y las alumnas ordenadas alfabéticamente por el primer apellido
        students = group.beneficiaries.all().order_by('last_name1')

        # Formateamos los datos en una lista de diccionarios
        students_data = []
        for s in students:
            # Construimos el nombre completo con el segundo apellido (en caso de que exista).
            full_name = f"{s.first_name} {s.last_name1} {s.last_name2 or ''}".strip()
            students_data.append({
                'id': s.id,
                'full_name': full_name,
            })
        return JsonResponse({'students': students_data})
    
    except Group.DoesNotExist:
            # En caso de que no se encuentre el grupo, devolvemos un mensaje de error
        return JsonResponse({'error': 'Grupo no encontrado'}, status=404)
