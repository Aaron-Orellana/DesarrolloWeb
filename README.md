# DesarrolloWeb

Este proyecto es parte del curso de Desarrollo Web.


# IMPORTANTE
    En este sprint 2 se agregara el login, por lo que es importante que sigan este paso al menos UNA VEZ, este paso lo pueden encontrar más detallado en el tutorial 2. Y para realizarlo, deben haber completado las migraciones del SPRINT 1.

### En su base de datos, deberan agregar el siguiente comando SQL
    INSERT INTO auth_group VALUES(1,'Admin');

### Creacion de super usuario (Para sus pruebas)
    python manage.py createsuperuser
Ejecutar este comando tambien es importante, para que pueda iniciar sesion.

### Añadir usuario a la base de datos
    INSERT INTO registration_profile VALUES(0, 'Default', 'Default', 1, 1)
Con estos comandos, tendremos nuestro super usuario para hacer las pruebas necesarias. ESTE USUARIO ES TEMPORAL

##### Para el sprint 3 deberiamos ser capaces de poder crear usuarios en la misma web, sin tener que poner comandos en la base de datos.