from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone # Necesario para la detección de la fecha actual
from .choices import NATIONALITY_CHOICES


# 1. MODELOS DE USUARIO Y ROLES (AUTH)


class Worker(AbstractUser):
    """Corresponde a la tabla Worker del UML."""
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha de alta")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de baja")
    active = models.BooleanField(default=True, verbose_name="Activo")
    role_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Rol del trabajador")
    
    class Meta:
        db_table = 'WORKER'
    


# 2. MODELOS PARA PROFESIONALES EXTERNOS (PSTC, UTS, tutores, etc.)


class WorkPlace(models.Model):
    place_name = models.CharField(max_length=100, verbose_name="Lugar de trabajo")

    class Meta:
        db_table = 'WORK_PLACE'

    def __str__(self):
        return self.place_name

class ExternalProfessional(models.Model):
    """Corresponde a ExternalProfessional del UML."""
    first_name = models.CharField(max_length=50, verbose_name="Nombre")
    last_name1 = models.CharField(max_length=50, verbose_name="Primer apellido")
    last_name2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Segundo apellido")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email")
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="Categoría")
    work_place = models.ForeignKey(WorkPlace, on_delete=models.SET_NULL, null=True, related_name='professionals')

    class Meta:
        db_table = 'EXTERNAL_PROFESSIONAL'

    def __str__(self):
        return f"{self.first_name} {self.last_name1}"


# 3.  MODELOS PARA EXPEDIENTES Y BENEFICIARIOS


class FamilyCase(models.Model):
    """ El número de expediente debe de ser único. """
    file_number = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        verbose_name="Nº Expediente", 
        help_text="Dejar este campo en blanco para que el sistema lo asigne automáticamente."
    )
    creation_date = models.DateField(auto_now_add=True, verbose_name="Fecha de creación")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")
    external_professional = models.ForeignKey(
        ExternalProfessional, on_delete=models.SET_NULL, null=True, blank=True, related_name='family_cases'
    )

    class Meta:
        db_table = 'FAMILY_CASE'

    def __str__(self):
        return f"Expediente {self.file_number}"
    def save(self, *args, **kwargs):
        # Si el usuario no introduce el número de expediente a mano
        if not self.file_number:
            current_year = timezone.now().year
            # Buscamos el último expediente que se haya creado.
            last_case = FamilyCase.objects.order_by('id').last()
            if last_case and last_case.file_number and '/' in last_case.file_number:
                #Extraemos el número final del ultimo expediente y lo pasamos a entero.
                last_number = int(last_case.file_number.split('/')[1])
                next_number = last_number + 1
            else:
                next_number = 1
            # Formatemos el nuevo número: año actual + barra + el nuevo número rellenado con ceros
            self.file_number = f"{current_year}/{str(next_number).zfill(3)}"
        
        super().save(*args, **kwargs)


class Beneficiary(models.Model):
  
    family_case = models.ForeignKey(FamilyCase, on_delete=models.CASCADE, related_name='beneficiaries')
    is_tutor = models.BooleanField(default=False, verbose_name="Es tutor/a legal")
    family_role = models.CharField(max_length=50, blank=True, null=True, verbose_name="Rol Familiar")
    first_name = models.CharField(max_length=50, verbose_name="Nombre")
    last_name1 = models.CharField(max_length=50, verbose_name="Primer apellido")
    last_name2 = models.CharField(max_length=50, blank=True, null=True, verbose_name="Segundo apellido")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    nationality = models.CharField(max_length=50, choices=NATIONALITY_CHOICES,default= 'España', verbose_name="Nacionalidad")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email")
    address = models.CharField(max_length=150, blank=True, null=True, verbose_name="Dirección")
    postal_code = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código Postal") # Es CharField para no perder el '0' como Álava o Burgos
    start_date = models.DateField(null=True, blank=True, verbose_name="Fecha de alta")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha de baja")
    active = models.BooleanField(default=True, verbose_name="Activo")
    derivation = models.BooleanField(default=False, verbose_name="Derivación")
    school = models.ForeignKey('WorkPlace', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Centro escolar")
    external_professionals = models.ManyToManyField('ExternalProfessional', blank=True, related_name='beneficiaries', verbose_name="Profesionales de referencia")


    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    class Meta:
        db_table = 'BENEFICIARY'
        verbose_name_plural = 'Beneficiaries'

    def __str__(self):
        return f"{self.first_name} {self.last_name1}"


# 4. GESTIÓN DE GRUPOS Y ASISTENCIA

class TrainingAction(models.Model):
    """Corresponde a TrainingAction del UML."""
    name = models.CharField(max_length=100, verbose_name="Nombre de la acción")
    type = models.CharField(max_length=50, verbose_name="Tipo")
    start_date = models.DateField(verbose_name="Fecha inicio")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha fin")
    start_time = models.TimeField(verbose_name="Hora de inicio")
    stop_time = models.TimeField(verbose_name="Hora de fin")
    worker = models.ForeignKey(Worker, on_delete=models.SET_NULL, null=True, related_name='training_actions')

    class Meta:
        db_table = 'TRAINING_ACTION'

    def __str__(self):
        return self.name

class Group(models.Model):
    """Corresponde a Group del UML. Incluye la relación automática ManyToMany."""
    name = models.CharField(max_length=50, verbose_name="Nombre del grupo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    training_action = models.ForeignKey(TrainingAction, on_delete=models.CASCADE, related_name='groups')
    beneficiaries = models.ManyToManyField(Beneficiary, related_name='enrolled_groups', blank=True)

    class Meta:
        db_table = 'GROUP'

    def __str__(self):
        return self.name

class Attendance(models.Model):
    """ Histórico diario asistencias."""
    ESTADOS = [
        ('PRESENT', 'Presente'),
        ('LATE', 'Retraso'),
        ('JUSTIFIED_ABSENCE', 'Falta Justificada'),
        ('UNJUSTIFIED_ABSENCE', 'Falta Injustificada'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='attendances')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(verbose_name="Fecha de la sesión")
    status = models.CharField(max_length=20, choices=ESTADOS, default='PRESENT', verbose_name="Estado")

    class Meta:
        db_table = 'ATTENDANCE'
        # Evitar duplicar asistencia del mismo niño en el mismo grupo el mismo día
        unique_together = ('group', 'beneficiary', 'date') 

    def __str__(self):
        return f"{self.beneficiary} - {self.date} ({self.get_status_display()})"