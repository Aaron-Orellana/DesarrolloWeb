from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Direccion, Departamento

@login_required
def direccion_listar(request):
    direcciones = Direccion.objects.all()
    return render(request, 'orgs/direccion_listar.html', {'direcciones': direcciones})

@login_required
def departamento_listar(request):
    departamentos = Departamento.objects.all()
    return render(request, 'orgs/departamento_listar.html', {'departamentos': departamentos})
