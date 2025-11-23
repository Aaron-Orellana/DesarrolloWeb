from django.shortcuts import render, redirect
from django.contrib import messages
from core.decorators import role_required
from .models import Ubicacion
from .forms import UbicacionForm


@role_required("Secpla")
def ubicacion_listar(request):
    ubicaciones = Ubicacion.objects.all().order_by("calle", "numero_casa")
    return render(request, "locations/ubicacion_list.html", {"ubicaciones": ubicaciones})


@role_required("Secpla")
def ubicacion_crear(request):
    form = UbicacionForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Ubicación creada correctamente.")
            return redirect("ubicacion_listar")
        messages.error(request, "Revisa los datos del formulario.")
    return render(request, "locations/ubicacion_form.html", {"form": form})
