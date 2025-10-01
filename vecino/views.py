from django.shortcuts import render
from .models import Vecino

def lista_vecinos(request):
    vecinos = Vecino.objects.all()
    return render(request, 'vecino/lista_vecinos.html', {'vecinos': vecinos})