
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
from .models import Group, Beneficiary, Attendance, FamilyCase, Worker, ExternalProfessional
from .forms import FamilyCaseForm, BeneficiaryForm
from datetime import date
import json

@login_required
def home_view(request):
    """Renderiza la plantilla base para comprobar la estructura de navegación"""
    return render(request, 'base.html')

@login_required
def attendance_view(request):
    """Muestra la pantalla de asistencia con los grupos y el alumnado correspondiente"""
    groups = Group.objects.all()
    
    # 1. Atrapamos lo que el usuario envía por la URL o ponemos valores por defecto
    selected_group_id = request.GET.get('group_id', '')
    # Por defecto se pone la fecha de hoy
    selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    search_query = request.GET.get('q', '')

    students = []
    registered_count = 0
    attended_count = 0

    # 2. Solo traemos alumnos y calculamos estadísticas si se ha elegido un grupo
    if selected_group_id:
        group = get_object_or_404(Group, id=selected_group_id)
        students_qs = group.beneficiaries.all()

        if search_query:
            students_qs = students_qs.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name1__icontains=search_query)
            )
        
        students = students_qs
        registered_count = students.count()

        saved_attendances = Attendance.objects.filter(
            group_id=selected_group_id,
            date=selected_date_str
        )
        attendance_dict = {att.beneficiary_id: att for att in saved_attendances}

        for student in students:
            student.current_attendance = attendance_dict.get(student.id)
            
        attended_count = saved_attendances.filter(status='PRESENT').count()


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

@login_required
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

@login_required
def update_attendance(request):
    """API interna: Recibe un POST de JavaScript y guarda la asistencia en la base de datos"""
    if request.method == 'POST':
        try:
            # 1. Desempaquetamos el JSON
            data = json.loads(request.body)
            student_id = data.get('student_id')
            group_id = data.get('group_id')
            date_string = data.get('date') 
            db_status = data.get('status') # Ahora recibimos 'PRESENT', 'LATE', etc. directamente
            incidence_time = data.get('incidence_time') # Atrapamos la hora

            # Validamos campos obligatorios
            if not all([student_id, group_id, date_string, db_status]):
                return JsonResponse({'success': False,'error': 'Faltan datos'}, status=400)
            
            # Si la hora llega vacía desde el HTML, la convertimos en un nulo válido para la BD
            if not incidence_time:
                incidence_time = None

            # 2. Guardamos o actualizamos en la base de datos
            Attendance.objects.update_or_create(
                group_id=group_id,
                beneficiary_id=student_id,
                date=date_string,
                defaults={
                    'status': db_status,
                    'incidence_time': incidence_time
                }
            )
            return JsonResponse({'success': True, 'message': 'Asistencia registrada correctamente'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        
    return JsonResponse({'error': 'Metodo no permitido'}, status=405)   

# Gestión de expedientes

@login_required
@permission_required('core.view_familycase', raise_exception=True) #Restringimos accesos a solo lectura para ciertos roles
def family_case_list(request):
    """Muestra la lista los expedientes familiares con un buscador"""
    # Si el usuario escribe algo en el buscador, filtramos los expedientes.
    query = request.GET.get('q', '')

    filter_status = request.GET.get('status', 'active')

    # 1. Filtramos primero por el estado
    if filter_status == 'archived':
        cases = FamilyCase.objects.filter(is_archived=True)
    else:
        cases = FamilyCase.objects.filter(is_archived=False)

    # 2. Si hay búsqueda, la aplicamos sobre esos expedientes
    if query:
        cases = cases.filter(
            Q(file_number__icontains=query) |
            Q(beneficiaries__first_name__icontains=query) |
            Q(beneficiaries__last_name1__icontains=query) |
            Q(beneficiaries__last_name2__icontains=query)
        ).distinct()

    # 3. Ordenamos por la fecha de creación
    cases = cases.order_by('-creation_date')

    return render(request, 'family_case_list.html', {
        'cases': cases, 
        'query': query,
        'current_status': filter_status
    })


@login_required
@permission_required('core.add_familycase', raise_exception=True)
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

@login_required
@permission_required('core.view_familycase', raise_exception=True)
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

@login_required
@permission_required('core.change_familycase', raise_exception=True)
def family_case_archive(request, case_id):
    """Archiva o desarchiva un expediente familiar completo"""
    case = get_object_or_404(FamilyCase, id=case_id)
    
    if request.method == 'POST':
        case.is_archived = not case.is_archiived
        case.save()
        return redirect('family_case_detail', case_id=case.id)
    
    return render(request, 'family_case_confirm_archive.html', {'case': case})

# --- GESTIÓN DE MIEMBROS DE UN EXPEDIENTE ---
@login_required
@permission_required('core.add_beneficiary', raise_exception=True)
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

@login_required
@permission_required('core.change_beneficiary', raise_exception=True)
def beneficiary_update(request, pk):
    """Carga el formulario de edición con los datos de un menor que  ya existe"""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    case = beneficiary.family_case  # Obtenemos el expediente al que pertenece el beneficiario

    if request.method == 'POST': 
        form = BeneficiaryForm(request.POST, instance=beneficiary)
        if form.is_valid():
            form.save()
            return redirect('beneficiary_detail', pk=beneficiary.pk)
    else:
        form = BeneficiaryForm(instance=beneficiary)
    
    return render(request, 'beneficiary_form.html', {'form': form, 'case': case})

@login_required
@permission_required('core.delete_beneficiary', raise_exception=True)
def beneficiary_delete(request, pk):
    """Pide confirmación y elimina un usuario de la base de datos"""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    case_id = beneficiary.family_case.id

    if request.method == 'POST':
        # Si el usuario confirma, se elimina
        beneficiary.delete()
        return redirect('family_case_detail', case_id=case_id)
    
    return render(request, 'beneficiary_confirm_delete.html', {'beneficiary': beneficiary})

# --- DIRECTORIO: USUARIOS (BENEFICIARIOS) ---
@login_required
def beneficiary_list(request):
    """Muestra el listado de usuarios/menores con buscador"""
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'last_name1')
    filter_status = request.GET.get('status', 'all')

    beneficiaries = Beneficiary.objects.all()

    #  Búsqueda textual
    
    if query:
        beneficiaries = Beneficiary.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name1__icontains=query) |
            Q(last_name2__icontains=query) |
            Q(family_case__file_number__icontains=query)
        ).distinct()
    
    # Filtrar por estado (Activo o baja)
    if filter_status == 'active':
        beneficiaries = beneficiaries.filter(active=True)
    elif filter_status == 'inactive':
        beneficiaries = beneficiaries.filter(active=False)

    # Ordenar y agrupar
    if sort_by == 'name_desc':
        beneficiaries = beneficiaries.order_by('-first_name', '-last_name1', '-last_name2')
    elif sort_by == 'date_desc':
        beneficiaries = beneficiaries.order_by('-start_date')
    elif sort_by == 'date_asc':
        beneficiaries = beneficiaries.order_by('start_date')
    elif sort_by == 'expediente':
        beneficiaries = beneficiaries.order_by('family_case__file_number', 'last_name1')
    else:
        beneficiaries = beneficiaries.order_by('last_name1', 'last_name2', 'first_name')

    return render(request, 'beneficiary_list.html', {
        'beneficiaries': beneficiaries, 
        'query': query, 
        'current_by': sort_by, 
        'current_status': filter_status,
    })

@login_required
def beneficiary_detail(request, pk):
    """Muestra la ficha detallada de un usuario/menor"""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    return render(request, 'beneficiary_detail.html', {'beneficiary': beneficiary})

@login_required
@permission_required('core.change_beneficiary', raise_exception=True)
def beneficiary_deactivate(request, pk):
    """Tramita la baja de un usuario/menor conservando su historial"""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)

    if request.method == 'POST':
        beneficiary.active = False  # Cambiamos el estado a baja
        beneficiary.enrolled_groups.clear() # Eliminamos todos los grupos
        beneficiary.save()

        return redirect('beneficiary_detail', pk=beneficiary.pk)
    
    return render(request, 'beneficiary_confirm_deactivate.html', {'beneficiary': beneficiary})

@login_required
@permission_required('core.change_beneficiary', raise_exception=True)
def beneficiary_activate(request, pk):
    """Reactiva a un usuario/menor que estaba de baja"""
    beneficiary = get_object_or_404(Beneficiary, pk=pk)
    
    if request.method == 'POST':
        beneficiary.active = True
        beneficiary.save()
        return redirect('beneficiary_detail', pk=beneficiary.pk)
        
    return render(request, 'beneficiary_confirm_activate.html', {'beneficiary': beneficiary})

# --- DIRECTORIO: CONTACTOS (PROFESIONALES EXTERNOS) ---

@login_required
def external_professional_list(request):
    """Muestra el listado de contactos de otras entidades con buscador"""
    query = request.GET.get('q', '')
    
    if query:
        professionals = ExternalProfessional.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name1__icontains=query) |
            Q(last_name2__icontains=query) |
            Q(category__icontains=query) |
            Q(work_place__place_name__icontains=query) # Permite buscar por el nombre de la entidad/colegio
        ).distinct().order_by('work_place__place_name', 'last_name1')
    else:
        professionals = ExternalProfessional.objects.all().order_by('work_place__place_name', 'last_name1')
        
    return render(request, 'external_professional_list.html', {'professionals': professionals, 'query': query})

@login_required
def external_professional_detail(request, pk):
    """Muestra la ficha detallada de un contacto externo"""
    professional = get_object_or_404(ExternalProfessional, pk=pk)
    return render(request, 'external_professional_detail.html', {'professional': professional})

# --- DIRECTORIO: TRABAJADORES (EQUIPO) ---
@login_required
def worker_list(request):
    """Muestra el listado del equipo de trabajadores con buscador"""
    query = request.GET.get('q', '')
    
    if query:
        # Nota: AbstractUser usa 'last_name' en lugar de 'last_name1'
        workers = Worker.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(role_name__icontains=query)
        ).distinct().order_by('first_name')
    else:
        workers = Worker.objects.all().order_by('first_name')
        
    return render(request, 'worker_list.html', {'workers': workers, 'query': query})

@login_required
def worker_detail(request, pk):
    """Muestra la ficha detallada de un trabajador"""
    worker = get_object_or_404(Worker, pk=pk)
    return render(request, 'worker_detail.html', {'worker': worker})

@login_required
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

@login_required
def group_list(request):
    """Muestra el listado de actividades y grupos activos"""
    query = request.GET.get('q', '')
    
    # Traemos los grupos y contamos cuántos beneficiarios tiene cada uno
    groups = Group.objects.select_related('training_action', 'training_action__worker').annotate(
        num_enrolled=Count('beneficiaries')
    ).order_by('training_action__start_date', 'name')
    
    if query:
        groups = groups.filter(
            Q(name__icontains=query) |
            Q(training_action__name__icontains=query)
        )
        
    return render(request, 'group_list.html', {'groups': groups, 'query': query})