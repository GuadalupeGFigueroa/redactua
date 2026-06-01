
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Group, Beneficiary, Attendance, FamilyCase
from .forms import FamilyCaseForm, BeneficiaryForm
from datetime import date
from django.db.models import Q, Count
import json


def home_view(request):
    """Renderiza la plantilla base para comprobar la estructura de navegación"""
    return render(request, 'base.html')

def attendance_view(request):
    """Muestra la pantalla de asistencia con los grupos y el alumnado correspondiente"""
    groups = Group.objects.all()
    from datetime import date
from django.db.models import Q

def attendance_view(request):
    """Muestra la pantalla de asistencia con los grupos y el alumnado correspondiente"""
    groups = Group.objects.all()
    
    # 1. Atrapamos lo que el usuario envía por la URL o ponemos valores por defecto
    selected_group_id = request.GET.get('group_id', '')
    # Por defecto, ponemos la fecha de hoy
    selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    search_query = request.GET.get('q', '')

    students = []
    registered_count = 0
    attended_count = 0

    # 2. Solo traemos alumnos y calculamos estadísticas si se ha elegido un grupo
    if selected_group_id:
        group = get_object_or_404(Group, id=selected_group_id)
        students_qs = group.beneficiaries.all()

        # Damos vida al buscador
        if search_query:
            students_qs = students_qs.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name1__icontains=search_query)
            )
        
        students = students_qs
        registered_count = students.count()

        # Damos vida al recuento real cruzando grupo, fecha y estado "Presente"
        attended_count = Attendance.objects.filter(
            group_id=selected_group_id,
            date=selected_date_str,
            status='PRESENT'
        ).count()

    context = {
        'groups': groups,
        'students': students,
        'selected_group_id': selected_group_id,
        'selected_date': selected_date_str,
        'search_query': search_query,
        'registered_count': registered_count,
        'attended_count': attended_count,
    }
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

            # 3. Lógica para guardar los datos 
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

# Gestión de expedientes

def family_case_list(request):
    """Muestra la lista los expedientes familiares con un buscador"""
    # Si el usuario escribe algo en el buscador, filtramos los expedientes.
    query = request.GET.get('q', '')

    if query:
        cases = FamilyCase.objects.filter(
            Q(file_number__icontains=query) |
            Q(beneficiaries__first_name__icontains=query) |
            Q(beneficiaries__last_name1__icontains=query) |
            Q(beneficiaries__last_name2__icontains=query)
        ).distinct().order_by('-creation_date') # Esto evita que salgan los expedientes duplicados si hay 2 alumnos hermanos
    else:
        # Si no se especifica, obtenemos todos los expeedientes ordenados del más nuevo al más antiguo
        cases = FamilyCase.objects.all().order_by('-creation_date')

    return render(request, 'family_case_list.html', {'cases': cases, 'query': query})

def family_case_create(request):
    """Maneja la creación de un nuevo expediente familiar"""
    # Si el usuario envía datos por POST, creamos el expediente
    if request.method == 'POST':
        form = FamilyCaseForm(request.POST)
        # Validamos el formulario
        if form.is_valid():
            form.save()
            return redirect('family_case_list')
        
    # Si el usuario envía datos por GET, mostramos el formulario vacio    
    else:
        form = FamilyCaseForm()

    return render(request, 'family_case_form.html', {'form': form})

def family_case_detail(request, case_id):
    """Muestra la ficha completa de un expediente y la lista de sus miembros"""
    # Buscamos la carpeta expediente y en caso de no existir se señala con un error 404.
    case = get_object_or_404(FamilyCase, id=case_id)

    # Obtenemos los miembros del expediente priorizando a los y las tutoras legales y a los menores por fecha de nacimiento
    members = case.beneficiaries.all().order_by('-is_tutor', 'birth_date')

    return render(request, 'family_case_detail.html', {
        'case': case,
        'members': members
    })

def beneficiary_create(request, case_id):
    """Añade un nuevo miembro (tutor/a o menor) a un expediente existente"""
    # Busca la carpeta (expediente) a la que vamos a vincular a esta persona
    case = get_object_or_404(FamilyCase, id=case_id)
    
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST)
        if form.is_valid():
            # 2. Guarda el formulario en memoria
            new_member = form.save(commit=False)
            
            # 3. Inyecta el expediente antes de guardarlo definitivamente
            new_member.family_case = case
            new_member.save()

            # Asignamos a que grupo va a asistir
            selected_groups = form.cleaned_data.get('groups')
            if selected_groups: 
                new_member.enrolled_groups.set(selected_groups)
            
            # 4. Devolvemos datos actualizados
            return redirect('family_case_detail', case_id=case.id)
    else:
        form = BeneficiaryForm()
        
    return render(request, 'beneficiary_form.html', {'form': form, 'case': case})

def statistics_view(request):
    """Genera reportes de asistencia filtrados por fecha y alumno"""
    
    # filtros
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    student_id = request.GET.get('student_id', '')

    # Filtramos asistencias
    attendances = Attendance.objects.all()

    if start_date:
        attendances = attendances.filter(date__gte=start_date)
    if end_date:
        attendances = attendances.filter(date__lte=end_date)
    if student_id:
        attendances = attendances.filter(beneficiary_id=student_id)

    # Conteo base de la base de datos
    stats_queryset = attendances.values('status').annotate(total=Count('id'))
    total_records = attendances.count()

    # Cálculo e inyección de los porcentajes
    stats = list(stats_queryset)
    for item in stats:
        if total_records > 0:
            # Calculamos y redondeamos a 1 decimal
            item['percentage'] = round((item['total'] / total_records) * 100, 1)
        else:
            item['percentage'] = 0

    #  Lista de menores para el desplegable
    students = Beneficiary.objects.filter(is_tutor=False).order_by('first_name', 'last_name1')

    
    context = {
        'stats': stats,
        'total_records': total_records,
        'students': students,
        'current_start': start_date,
        'current_end': end_date,
        'current_student': student_id,
    }
    
    return render(request, 'statistics.html', context)