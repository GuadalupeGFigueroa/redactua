
from django.shortcuts import render
from django.http import JsonResponse
from .models import Group, Beneficiary, Attendance
import json

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

def update_attendance(request):
    """API interna: Recibe un POST de JavaScript y guarda la asistencia en la base de datos"""
    # Solo aceptamos los datos si vienen en el método POST (envío de datos)
    if request.method == 'POST':
        try:
            # 1. Desempaquetamos el JSON que nos envvía JavaScript
            data = json.loads(request.body)
            student_id = data.get('student_id')
            group_id = data.get('group_id')
            date_string = data.get('date') 
            status_text = data.get('status')

            # Validamos que nos han llegado todos los datos que necesitamos
            if not all([student_id, group_id, date_string, status_text]):
                return JsonResponse({'success': False,'error': 'Faltan datos'}, status=400)
            
            # 2. Traducimos el texto del botón al formato de la base de datos
            status_mapping = {
                'Asiste' : 'PRESENT',
                'Retraso' : 'LATE',
                'Falta' : 'UNJUSTIFIED_ABSENCE',
            }
            db_status = status_mapping.get(status_text, 'PRESENT')

            # 3. Lógica para guardar los datos (DJANGO ORM)
            # En caso de existir un registro, lo actualiza, sino lo crea.
            Attendance.objects.update_or_create(
                group_id=group_id,
                beneficiary_id=student_id,
                date=date_string,
                defaults={'status': db_status}
            )
            return JsonResponse({'success': True, 'message': 'Asistencia registrada correctamente'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
    #Medida de seguridad si alguien intenta entrar por URL
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)       

