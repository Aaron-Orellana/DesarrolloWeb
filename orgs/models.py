from django.db import models
from registration.models import Profile

class Secpla(models.Model):
    #pk
    secpla_id = models.BigAutoField(
        primary_key=True,
        db_column='Secpla_id'
    )

    #FK
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='secplas',
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Secpla"
        verbose_name_plural = "Secplas"
        ordering = ["nombre"]

    def __str__(self):
        if self.profile:
            return f"{self.nombre} ({self.profile})"
        return self.nombre

class Departamento(models.Model):
    #PK
    departamento_id = models.BigAutoField(
	primary_key=True,
	db_column='Departamento_ID'
    )

    #Campos simples
    nombre = models.CharField(max_length=150)
    estado = models.CharField(max_length=20, default='Activo')
    
    #FK
    direccion = models.ForeignKey(
        'Direccion', 
        on_delete=models.PROTECT,
        db_column='Direccion_id',
        related_name='Departamento'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='departamentos',
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["direccion", "nombre"], name="unique_departamento_por_direccion")
        ]

    def __str__(self):
        return f"{self.nombre} ({self.direccion})"
    
    
class Cuadrilla(models.Model):
    cuadrilla_id = models.AutoField(primary_key=True) 
    nombre = models.CharField(max_length=100) 
    estado = models.CharField(max_length=20, default='Activo') 
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        db_column='Departamento_id',
        related_name='Cuadrilla'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='cuadrillas',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cuadrilla'
        verbose_name_plural = 'Cuadrillas'

class Direccion(models.Model):
    direccion_id = models.AutoField(primary_key=True, db_column='Direccion_id')
    nombre = models.CharField(max_length=150, unique=True)
    estado = models.CharField(max_length=20, default='Activo')

    # Relación con el perfil responsable
    profile = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='direcciones',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Territorial(models.Model):
    #PK
    territorial_id = models.BigAutoField(
	primary_key=True,
	db_column='Territorial_ID'
    )
    #Campos libres
    nombre = models.CharField(max_length=100, unique=True)
    
    #FK
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='territoriales',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Territorial"
        verbose_name_plural = "Territoriales"
        ordering = ["nombre"]

    def __str__(self):
        if self.profile:
            return f"{self.nombre} ({self.profile})"
        return self.nombre
