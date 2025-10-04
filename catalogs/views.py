from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Incidencia
from orgs.models import Direccion, Departamento
from django.core.paginator import Paginator #Objeto para paginar resultados (usado en vistas)

@login_required
def incidencia_crear(request):
    direcciones = Direccion.objects.all()
    departamentos = Departamento.objects.all() 
    return render(request, 'incidencia_crear.html', {  
        'direcciones': direcciones,
        'departamentos': departamentos,
    })

@login_required
def incidencia_guardar(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        direccion_id = request.POST.get('direccion')
        departamento_id = request.POST.get('departamento')

        if not nombre:
            messages.error(request, 'El nombre de la incidencia es requerido.')
            return redirect('incidencia_crear')

        if not direccion_id or not departamento_id:
            messages.error(request, 'Debe seleccionar una dirección y un departamento.')
            return redirect('incidencia_crear')

        try:
            direccion = Direccion.objects.get(id=direccion_id)
        except Direccion.DoesNotExist:
            messages.error(request, 'La dirección seleccionada no existe.')
            return redirect('incidencia_crear')

        try:
            departamento = Departamento.objects.get(id=departamento_id)
        except Departamento.DoesNotExist:
            messages.error(request, 'El departamento seleccionado no existe.')
            return redirect('incidencia_crear')

        if departamento.direccion != direccion:
            messages.error(request, 'El departamento seleccionado no pertenece a la dirección elegida.')
            return redirect('incidencia_crear')

        incidencia = Incidencia(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            departamento=departamento,
        )
        incidencia.save()

        messages.success(request, 'Incidencia creada exitosamente.')
        return redirect('incidencia_lista')
    
    return redirect('incidencia_crear')
@login_required
def incidencia_listar(request):
    incidencias_list = Incidencia.objects.all().order_by('-incidencia_id')  #ID auto incrementable, mas bajo primero
    paginator = Paginator(incidencias_list, 10)
    page_number = request.GET.get('page')
    incidencias = paginator.get_page(page_number)
    
    return render(request, 'incidencia_lista.html', {
        'incidencias': incidencias,
    })