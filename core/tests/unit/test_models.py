from django.test import TestCase
from core.models import FamilyCase
from datetime import date

class FamilyCaseModelTest(TestCase):
    
    def test_file_number_generation(self):
        """Comprueba que el número de expediente se genera con el formato correcto (Año/Correlativo) y suma secuencialmente."""
        
        # 1. PREPARAR: Creamos nuestro primer expediente de prueba
        case1 = FamilyCase.objects.create()
        
        # 2. COMPROBAR: Verificamos que el formato es AñoActual/001
        current_year = date.today().year
        self.assertEqual(case1.file_number, f"{current_year}/001")
        
        # 3. ACTUAR: Creamos un segundo expediente
        case2 = FamilyCase.objects.create()
        
        # 4. COMPROBAR: Verificamos que el contador ha sumado 1 correctamente
        self.assertEqual(case2.file_number, f"{current_year}/002")