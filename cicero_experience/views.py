from django.shortcuts import render
from django.shortcuts import redirect
from django.db import DatabaseError

from .models import Visitantes

from django.conf import settings


def index(request):
    error_message = None
    faixas_etarias_choices = Visitantes.FAIXAS_ETARIAS
    grupo_ = Visitantes.OPCOES_GRUPO
    generos = Visitantes.OPCOES_GENERO
    cor_racas = Visitantes.OPCOES_COR_RACA


    if request.method == "POST":
        pais = request.POST.get("pais", "").strip()
        estado = request.POST.get("estado", "").strip()
        cidade = request.POST.get("cidade", "").strip()

        faixa_etaria = request.POST.get("faixa_etaria", "").strip()

        fingerprint = request.POST.get("fingerprint")

        grupo = request.POST.get("grupo", "").strip()
        genero = request.POST.get("genero", "").strip()
        cor_raca = request.POST.get("cor_raca", "").strip()

        if not fingerprint:
            error_message = "Não foi possível identificar o visitante."
        else:

            try:
                Visitantes.objects.create(
                    fingerprint=fingerprint,
                    pais=pais,
                    estado=estado,
                    cidade=cidade,
                    faixa_etaria=faixa_etaria,
                    grupo=grupo, 
                    genero=genero,
                    cor_raca=cor_raca 
                )
                return redirect("index")
            except DatabaseError:
                error_message = "Ocorreu um erro ao salvar no banco. Tente novamente."

    visitantes_list = Visitantes.objects.order_by("-data_chekin")[:5]
    return render(request, "cicero_experience/index.html", {
        "visitantes_list": visitantes_list,
        "faixas_etarias_choices": faixas_etarias_choices,
        "grupo_": grupo_,
        "generos": generos,
        "cor_racas": cor_racas,
        "error_message": error_message,
        "csc_api_key": settings.CSC_API_KEY,
    })
