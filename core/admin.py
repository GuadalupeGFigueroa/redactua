from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Worker, WorkPlace, ExternalProfessional, FamilyCase, Beneficiary, TrainingAction, Group, Attendance
)

# La clase worker hereda de UserAdmin, una clase especial de Django que nos permite personalizar el admin.
admin.site.register(Worker, UserAdmin)

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    filter_horizontal = ('external_professionals',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('beneficiaries',)

# Registramos el resto de modelos para la obtención de datos.
admin.site.register(WorkPlace)
admin.site.register(ExternalProfessional)
admin.site.register(FamilyCase)
admin.site.register(TrainingAction)
admin.site.register(Attendance)


