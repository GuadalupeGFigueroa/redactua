from django.test import TestCase
from core.forms import BeneficiaryForm
from datetime import date, timedelta

class BeneficiaryFormTest(TestCase):
    
    def test_future_birth_date_is_invalid(self):
        """Comprueba que el formulario rechaza fechas de nacimiento en el futuro"""
        
        # 1. PREPARAR: Calculamos la fecha de mañana
        future_date = date.today() + timedelta(days=1)
        
        # Simulamos los datos que enviaría el usuario por POST
        # (Si tienes otros campos obligatorios sin valor por defecto en tu modelo, 
        # como el DNI, añádelos a este diccionario para que no falle por otra causa)
        form_data = {
            'first_name': 'Viajero',
            'last_name1': 'Del Tiempo',
            'birth_date': future_date,
            'is_tutor': False,
        }
        
        # 2. ACTUAR: Le pasamos los datos al formulario
        form = BeneficiaryForm(data=form_data)
        
        # 3. COMPROBAR: El formulario NO debe ser válido
        self.assertFalse(form.is_valid())
        
        # Además, comprobamos que el error salta específicamente en la fecha
        self.assertIn('birth_date', form.errors)