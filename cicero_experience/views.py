from django.shortcuts import render

from .models import Visitantes


def index(request):
    visitantes_list = Visitantes.objects.order_by("-data_chekin")[:5]
    context = {"visitantes_list": visitantes_list}
    return render(request,"cicero_experience/index.html")
