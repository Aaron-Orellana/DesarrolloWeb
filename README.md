# DesarrolloWeb

Este proyecto es parte del curso de Desarrollo Web.


# IMPORTANTE
1. Como estamos modularizando las apps, para importar una foreign key, recomiendo hacerlo de esta manera.

``` 
    # FKs
    direccion = models.ForeignKey(
        'orgs.Direccion',   # app orgs, modelo Direccion
        on_delete=models.PROTECT,
        db_column='Direccion_id',
        related_name='incidencias'
    )
```
Llamas a la app y al modelo, para los atributos que no son llaves foraneas. no es necesario cambiar.

2. Si no tienes la ultima version te recomiendo hacer las migraciones 
```bash
python manage.py makemigrations
python manage.py migrate
```
Con esto nos aseguramos de que tu proyecto pueda funcionar. Además recordar, añadir el archivo settings.py, actualmente esta como settings.txt, este archivo settings.py debe ir en la carpeta municipalidad. y debes ingresarle solamente tus datos de base de datos.

### ADVERTENCIA
En caso de que se añada nueva app, o en tu commit modifiques tu settings.py, hazlo saber modificando el settings.txt, para que la siguiente persona no tenga errores extraños.

Mientras todos colaboramos, menos problemas tendremos.
Este README se ira modificando a gusto y peticiones del profe

## Descarga del proyecto

```bash
git clone https://github.com/Aaron-Orellana/DesarrolloWeb.git
cd DesarrolloWeb
```

## Instalación y ejecución con Conda

1. Crea el entorno conda:
    ```bash
    conda create -n desarrolloweb python=3.11
    conda activate desarrolloweb
    ```

2. Instala las dependencias:
    ```bash
    conda install --file requirements.txt
    ```

3. Ejecuta el proyecto:
    ```bash
    python manage.py runserver
    ```


