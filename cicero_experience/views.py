from django.http import HttpResponse
from django.template import loader

from .models import Visitantes


def index(request):
    visitantes_list = Visitantes.objects.order_by("-data_chekin")[:5]
    template = loader.get_template("cicero_experience/index.html")
    context = {"visitantes_list": visitantes_list}
    return HttpResponse(template.render(context, request))
