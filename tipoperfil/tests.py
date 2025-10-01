from django.test import TestCase
from .models import TipoPerfil
from django.db import IntegrityError

class TipoPerfilModelTest(TestCase):

    def test_crear_tipo_perfil(self):
        perfil = TipoPerfil.objects.create(nombre="Administrador")
        self.assertEqual(perfil.nombre, "Administrador")

    def test_unicidad_nombre(self):
        TipoPerfil.objects.create(nombre="Usuario")
        with self.assertRaises(IntegrityError):
            TipoPerfil.objects.create(nombre="Usuario")  # Debe fallar por unique
