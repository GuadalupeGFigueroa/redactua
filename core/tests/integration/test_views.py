from django.contrib.auth.models import Permission
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model 
from core.models import FamilyCase

# Le pedimos a Django que nos traiga tu modelo personalizado (Worker)
User = get_user_model()

class SecurityViewsTest(TestCase):
    def setUp(self):
        """Preparamos el entorno antes de cada prueba"""
        # 1. Creamos el navegador virtual
        self.client = Client()
        
        # 2. Creamos un usuario "Educador" usando tu modelo Worker
        self.user_educador = User.objects.create_user(
            username='educador_test', 
            password='password123'
        )
        read_familycase_permission = Permission.objects.get(codename='view_familycase')
        self.user_educador.user_permissions.add(read_familycase_permission)
        
        # 3. Creamos un expediente de prueba
        self.case = FamilyCase.objects.create()

    def test_unauthenticated_user_redirects_to_login(self):
        """Comprueba que un visitante anónimo no puede ver la lista de expedientes"""
        
        # Intentamos entrar a la URL sin iniciar sesión
        url = reverse('family_case_list')
        response = self.client.get(url)
        
        # Comprobamos que el sistema nos expulsa hacia el login (Código HTTP 302: Redirección)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_authenticated_user_can_access_list(self):
        """Comprueba que un usuario con sesión iniciada sí puede ver los expedientes"""
        
        # Iniciamos sesión con nuestro educador
        self.client.login(username='educador_test', password='password123')
        
        # Intentamos entrar de nuevo
        url = reverse('family_case_list')
        response = self.client.get(url)
        
        # Comprobamos que el acceso es correcto (Código HTTP 200: OK)
        self.assertEqual(response.status_code, 200)