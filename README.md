# DesarrolloWeb

Este proyecto es parte del curso de Desarrollo Web.


## Organización de los modelos dentro de las Apps

### 🧑‍💼 **Accounts**
- **Usuario**
- **Perfil**
- **Tipo_perfil**

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

## Configuración Inicial

# IMPORTANTE
En este sprint 2 se agregara el login, por lo que es importante que sigan este paso al menos UNA VEZ, este paso lo pueden encontrar más detallado en el tutorial 2. Y para realizarlo, deben haber completado las migraciones del SPRINT 1.

### En su base de datos, deberan agregar el siguiente comando SQL
```sql
INSERT INTO auth_group VALUES(1,'Admin');
```

### Creacion de super usuario (Para sus pruebas)
```bash
python manage.py createsuperuser
```
Ejecutar este comando tambien es importante, para que pueda iniciar sesion.

### Añadir usuario a la base de datos
```sql
INSERT INTO registration_profile VALUES(0, 'Default', 'Default', 1, 1);
```
Con estos comandos, tendremos nuestro super usuario para hacer las pruebas necesarias. ESTE USUARIO ES TEMPORAL

## Roadmap

### ✅ Sprint 1
- Configuración inicial del proyecto
- Modelos base de datos
- Migraciones iniciales

### 🔄 Sprint 2 (Actual)
- Sistema de login y autenticación
- Gestión de usuarios básica
- Interfaz de administración

### 📋 Sprint 3 (Próximo)
- Registro de usuarios desde la web
- Eliminación de comandos SQL manuales
- Sistema completo de gestión de usuarios

## Instalación y Uso

1. **Clonar el repositorio**
```bash
git clone [repository-url]
cd DesarrolloWeb
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

---
**Nota**: Para el sprint 3 deberíamos ser capaces de poder crear usuarios en la misma web, sin tener que poner comandos en la base de datos.

**Como cargar datos de prueba**
python manage.py loaddata orgs/fixtures/direcciones.json
python manage.py loaddata orgs/fixtures/departamentos.json
python manage.py loaddata orgs/fixtures/cuadrillas.json