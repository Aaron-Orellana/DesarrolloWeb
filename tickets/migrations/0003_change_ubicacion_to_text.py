from django.db import migrations, models


def copy_ubicacion_to_text(apps, schema_editor):
    SolicitudIncidencia = apps.get_model('tickets', 'SolicitudIncidencia')
    for solicitud in SolicitudIncidencia.objects.select_related('ubicacion'):
        ubicacion_obj = getattr(solicitud, 'ubicacion', None)
        if ubicacion_obj:
            solicitud.ubicacion_text = str(ubicacion_obj)
            solicitud.save(update_fields=['ubicacion_text'])


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0002_alter_solicitudincidencia_cuadrilla_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitudincidencia',
            name='ubicacion_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(copy_ubicacion_to_text, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='solicitudincidencia',
            name='ubicacion',
        ),
        migrations.RenameField(
            model_name='solicitudincidencia',
            old_name='ubicacion_text',
            new_name='ubicacion',
        ),
        migrations.AlterField(
            model_name='solicitudincidencia',
            name='ubicacion',
            field=models.CharField(blank=True, max_length=255, null=True, db_column='Ubicacion'),
        ),
    ]
