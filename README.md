# DesarrolloWeb

Este proyecto es parte del curso de Desarrollo Web.
La rama que estas viendo ahora corresponde al sprint5

## Organización de los modelos dentro de las Apps
    Se ha removido la app Accounts para remplazarlo por las tablas nativas de DJANGO.

### 📚 **Catalogs**
- **Incidencia** (Tipos)

### 📍 **Locations**
- **Ubicación**
- **Vecino**

### 🏢 **Orgs**
- **Dirección**
- **Departamento**
- **Cuadrilla**
- **Territorial**

### 📝 **Surveys**
- **Pregunta**
- **Encuesta**
- **Respuesta**

### 🎫 **Tickets**
- **Solicitud_Incidencia**
- **Historial_Estado_Encuesta** (historial de la solicitud)
- **Multimedia**

### Registration
- **Profile**


## Configuración Inicial

# IMPORTANTE
**Recomiendo borrar toda su base de datos, y crear una nueva para empezar a trabajar.**

En este sprint 4 ya hay un login funcionado con el flujo que los profesores quieren. Por lo que una vez hecho las migraciones `python manage.py migrate` deberan cargar al usuario de prueba `python manage.py loaddata registration/fixtures/admin_user.json`.
Al entrar a la pagina, el nombre que pondran de username es `admin` y la contraseña es `Admin123!`, respetando la mayuscula.
Ya despues podran crear otros usuarios dentro de la seccion usuarios.

## Instalación y Uso

1. **Clonar el repositorio**
```bash
git clone [https://github.com/Aaron-Orellana/DesarrolloWeb.git]
cd DesarrolloWeb
git checkout sprint4
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecutar migraciones**
```bash
python manage.py migrate
```

4. **Seguir los pasos de configuración inicial** (ver sección anterior)

5. **Ejecutar el servidor**
```bash
python manage.py runserver
```

6. **Añadir media al settings.py**
```bash
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```


**Como cargar datos de prueba**

```
python manage.py loaddata orgs/fixtures/dev_seed.json

este ya se queda obsoleto -> python manage.py loaddata registration/fixtures/admin_user.json
```

Usuario secpla
user: `admin_secpla`
pass: `pass1234`

Usuario departamento
user: `dep_infra`
pass: `pass1234`

Usuario direccion
user: `dir_obras`
pass: `pass1234`

Usuario Cuadrilla
user: `cuadrilla_infra`
pass: `pass1234`

Usuario territorial
user: `territorial_norte`
pass: `pass1234`

# 🔐 Control de acceso por roles (core/decorators.py)

Este módulo permite restringir el acceso a vistas según el grupo (rol) del usuario.

---

## 🧩 Decorador `@role_required` (vistas basadas en función)

### Parametros que acepta:

Secpla
Direcciones
Departamentos
Cuadrillas
Territoriales


## 📘 Ejemplo básico
```python
from core.decorators import role_required
from django.shortcuts import render

@role_required("Secpla", "Direccion")
def panel_admin(request):
    return render(request, "panel_admin.html")
```

# 🧱 Uso de `RoleRequiredMixin` en vistas genéricas basadas en clases

Este mixin permite restringir el acceso a **vistas genéricas basadas en clases (CBV)** según los grupos del usuario.

---

## 📘 Ejemplo básico

```python

from django.views.generic import ListView, DetailView
from core.decorators import RoleRequiredMixin
from .models import Usuario

class UsuarioListView(RoleRequiredMixin, ListView):
    model = Usuario
    template_name = "usuarios/lista.html"
    allowed_roles = ["Administradores", "Supervisores"]
```

**ya no es necesario en las clases poner LoginRequiredMixin**

# Guía de Uso de Botones y Iconos
Explicacion de **cómo implementar los estilos definidos en `botones.css`**, cómo usar los **iconos de Bootstrap Icons**.
## 1. Variables Globales en `botones.css`
En `:root` se definen colores reutilizables para los botones, estas variables permiten cambiar la paleta de colores desde un solo lugar
## 2. Clase Base: `.btn-accion`
Todos los botones comparten esta clase:
Esta clase asegura que **todos los botones tengan el mismo estilo base**.
## 3. Botones con Colores Específicos
**Crear / Editar / Eliminar / Volver**
## 4. Iconos (Bootstrap Icons)
Ejemplos de iconos:
- **Crear:** `<i class="bi bi-plus-circle"></i>`
- **Editar:** `<i class="bi bi-pencil-square"></i>`
- **Ver:** `<i class="bi bi-eye"></i>`
- **Volver:** `<i class="bi bi-arrow-left-circle"></i>`
- **Eliminar:** `<i class="bi bi-trash"></i>`
- **Actualizar:** `<i class="bi bi-arrow-repeat"></i>`
- **Enviar:** `<i class="bi bi-send"></i>`
- **Bloquear:** `<i class="bi bi-lock-fill"></i>`
- **Desbloquear:** `<i class="bi bi-unlock-fill"></i>`
- **Guardar:** `<i class="bi bi-save"></i>`
## 5. Ejemplo de Uso Completo
Botón para **volver al dashboard**:

```html
<a href="{% url 'dashboard_cuadrilla' %}" class="btn btn-accion btn-volver">
    <i class="bi bi-arrow-left-circle"></i> Volver
</a>
```
- `class="btn"` -> Clase base de Bootstrap.
- `btn-accion` -> Aplica el estilo general de botones (bordes, alineación, tipografía).
- `btn-volver` -> Cambia los colores a la paleta específica del botón "Volver".

**Nota:** Estos colores podrían cambiar en un futuro en caso de dificultades al visualizar en los fondos.
