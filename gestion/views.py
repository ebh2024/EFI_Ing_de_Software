from django.shortcuts import render
from .models import Vuelo

def lista_vuelos(request):
    vuelos = Vuelo.objects.all()
    return render(request, 'gestion/lista_vuelos.html', {'vuelos': vuelos})
