from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Encuesta

@login_required
def encuesta_listar(request):
    encuestas = Encuesta.objects.all()
    return render(request, 'surveys/encuesta_listar.html', {'encuestas': encuestas})

# Create your views here.
