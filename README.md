# DesarrolloWeb

Este proyecto es parte del curso de Desarrollo Web.


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