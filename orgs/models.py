from django.db import models
from registration.models import Profile
from django.utils import timezone

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
    estado = models.BooleanField(default=True, db_column='Estado')
    
    #FK
    direccion = models.ForeignKey(
        'Direccion', 
        on_delete=models.PROTECT,
        db_column='Direccion_id',
        related_name='Departamento'
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
    estado = models.BooleanField(default=True, db_column='Estado')
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        db_column='Departamento_id',
        related_name='Cuadrilla'
    )

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Cuadrilla'
        verbose_name_plural = 'Cuadrillas'

class Direccion(models.Model):
    direccion_id = models.AutoField(primary_key=True, db_column='Direccion_id')
    nombre = models.CharField(max_length=150, unique=True)
    estado = models.BooleanField(default=True, db_column='Estado')

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

class DireccionMembership(models.Model):
    #PK
    direccion_membership_id = models.BigAutoField(
        primary_key=True,
        db_column='Direccion_Membership_ID'
    )

    #FK
    direccion = models.ForeignKey(
        Direccion,
        on_delete=models.PROTECT,
        db_column='Direccion_id',
        related_name='memberships'
    )
    es_encargado = models.BooleanField(default=False, db_column='Es_Encargado')
    desde = models.DateField(db_column='Desde', default=timezone.now)

    usuario_id = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='direccion_memberships'
    )

    class Meta:
        verbose_name = "Dirección Membership"
        verbose_name_plural = "Dirección Memberships"

    def __str__(self):
        return f"Membership for {self.direccion}"
    
class DepartamentoMembership(models.Model):
    #PK
    departamento_membership_id = models.BigAutoField(
        primary_key=True,
        db_column='Departamento_Membership_ID'
    )

    #FK
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        db_column='Departamento_id',
        related_name='memberships'
    )
    es_encargado = models.BooleanField(default=False, db_column='Es_Encargado')
    desde = models.DateField(db_column='Desde', default=timezone.now)

    usuario_id = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='departamento_memberships'
    )

    class Meta:
        verbose_name = "Departamento Membership"
        verbose_name_plural = "Departamento Memberships"

    def __str__(self):
        return f"Membership for {self.departamento}"
    
class CuadrillaMembership(models.Model):
    #PK
    cuadrilla_membership_id = models.BigAutoField(
        primary_key=True,
        db_column='Cuadrilla_Membership_ID'
    )
    #FK
    cuadrilla = models.ForeignKey(
        Cuadrilla,
        on_delete=models.PROTECT,
        db_column='Cuadrilla_id',
        related_name='memberships'
    )
    desde = models.DateField(db_column='Desde', default=timezone.now)

    usuario_id = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        db_column='Usuario_id',
        related_name='cuadrilla_memberships'
    )

    class Meta:
        verbose_name = "Cuadrilla Membership"
        verbose_name_plural = "Cuadrilla Memberships"

    def __str__(self):
        return f"Membership for {self.cuadrilla}"
