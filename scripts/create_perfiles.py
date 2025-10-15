import os
import sys
import django

# ---- agregar la carpeta raíz al path ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # scripts/
sys.path.append(os.path.dirname(BASE_DIR))  # agrega la raíz DesarrolloWeb

# ---- configurar Django ----
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")  # solo 'settings', no 'DesarrolloWeb.settings'
django.setup()

from django.contrib.auth.models import User
from accounts.models import TipoPerfil, Perfil, Usuario

# ---- creación de tipos de perfil ----
tipos_necesarios = ["Administrador", "Empleado", "Vecino"]
for nombre in tipos_necesarios:
    obj, created = TipoPerfil.objects.get_or_create(nombre=nombre)
    if created:
        print(f"✅ TipoPerfil creado: {nombre}")
    else:
        print(f"⚠ TipoPerfil ya existía: {nombre}")

# ---- creación de usuarios y perfiles ----
usuarios = [
    {"username": "admin_muni", "email": "admin@muni.cl", "password": "Admin123!", "tipo": "Administrador"},
    {"username": "empleado_rrhh", "email": "rrhh@muni.cl", "password": "Empleado123!", "tipo": "Empleado"},
    {"username": "vecino1", "email": "vecino1@muni.cl", "password": "Vecino123!", "tipo": "Vecino"},
]

for u in usuarios:
    user_obj, created = User.objects.get_or_create(username=u["username"], defaults={"email": u["email"]})
    if created:
        user_obj.set_password(u["password"])
        user_obj.save()
        print(f"✅ Usuario creado: {u['username']}")
    else:
        print(f"⚠ Usuario ya existía: {u['username']}")

    tipo = TipoPerfil.objects.get(nombre=u["tipo"])
    perfil_obj, perfil_created = Perfil.objects.get_or_create(usuario=user_obj, defaults={"tipo_perfil": tipo})
    if perfil_created:
        print(f"✅ Perfil creado para: {u['username']} ({u['tipo']})")
    else:
        print(f"⚠ Perfil ya existía para: {u['username']}")
