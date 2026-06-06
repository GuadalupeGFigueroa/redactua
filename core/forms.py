from django import forms
from .models import FamilyCase, Beneficiary, Group, ExternalProfessional
from django.core.exceptions import ValidationError
from datetime import date

class FamilyCaseForm(forms.ModelForm):
    """Formulario para crear o editar el expediente familiar"""
    class Meta:
        model = FamilyCase
        fields = ['file_number', 'external_professional', 'notes']

        # Inyectamos las clases de bootstrap 
        widgets = {
            'file_number': forms.TextInput(attrs={'class': 'form-control bg-light border-0', 'placeholder': 'Ejemplo: 2026/080'}),
            'external_professional': forms.Select(attrs={'class': 'form-select bg-light border-0'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-light border-0', 'rows': 3, 'placeholder': 'Observaciones generales del núcleo familiar...'}),
        }
class BeneficiaryForm(forms.ModelForm):
    """Formular para crear o editar un beneficiario"""
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Asignar a grupos de asistencia"
    )

    class Meta:
        model = Beneficiary
        
        fields = [
            'is_tutor', 'family_role', 'first_name', 'last_name1', 'last_name2', 'birth_date', 
            'nationality', 'phone_number', 'email', 'address', 'postal_code', 
            'school', 'groups','derivation', 'notes'
        ]

        widgets = {
            'is_tutor': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
            'family_role': forms.TextInput(attrs={'class': 'form-control bg-light', 'placeholder': 'Ejemplo: Padre, Madre, Abuela, etc.'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'last_name1': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'last_name2': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control bg-light', 'type': 'date'}), # Agregamos el atributo 'type': 'date' para que salga el calendario nativo del navegador.
            'nationality': forms.Select(attrs={'class': 'form-select bg-light'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-light'}),
            'address': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control bg-light'}),
            'school': forms.Select(attrs={'class': 'form-select bg-light'}),
            'derivation': forms.CheckboxInput(attrs={'class': 'form-check-input border-dark'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-light', 'rows': 3}),
        }
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return birth_date

class ExternalProfessionalForm(forms.ModelForm):
    class Meta:
        model = ExternalProfessional
        fields = ['first_name', 'last_name1', 'last_name2', 'phone_number', 'email', 'category', 'work_place']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name1': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name2': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'work_place': forms.Select(attrs={'class': 'form-select'}),
        }
