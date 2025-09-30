# DesarrolloWeb

Este proyecto es parte del curso de Desarrollo Web.


# IMPORTANTE
Si no tienes la ultima version te recomiendo (por: Martin Ferreira) hacer las migraciones 
```bash
python manage.py makemigrations
python manage.py migrate
```
Con esto nos aseguramos de que tu proyecto pueda funcionar. Además recordar, añadir en el txt, los cambios que hayas hecho en tu settings.py
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


