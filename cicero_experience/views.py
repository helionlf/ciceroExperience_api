from django.shortcuts import render, redirect
from django.db import DatabaseError
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Visitantes
from django.contrib import messages
from django.conf import settings


@ensure_csrf_cookie
def index(request):
    faixas_etarias_choices = Visitantes.FAIXAS_ETARIAS
    grupo_ = Visitantes.OPCOES_GRUPO
    generos = Visitantes.OPCOES_GENERO
    cor_racas = Visitantes.OPCOES_COR_RACA

    hoje = timezone.localdate()

    if request.method == "POST":
        action = request.POST.get("action")
        fingerprint = request.POST.get("fingerprint")

        if not fingerprint:
            messages.error(request, "Não foi possível identificar o visitante.")
        else:
            try:
                visitante_existente = Visitantes.objects.filter(
                    fingerprint=fingerprint,
                    data=hoje
                ).first()

                if action == "checkin":
                    if visitante_existente:
                        messages.error(request, "Você já fez o check-in hoje.")
                    else:
                        Visitantes.objects.create(
                            fingerprint=fingerprint,
                            pais="",
                            estado="",
                            cidade="",
                            faixa_etaria="nao_informado",
                            grupo="desconhecido",
                            genero="nao_informado",
                            cor_raca="nao_informado"
                        )
                        messages.success(request, "Seu Check-in foi realizado com sucesso!")
                        return redirect("index")
                    
                elif action == "form":
                    pais = request.POST.get("pais", "").strip()
                    estado = request.POST.get("estado", "").strip()
                    cidade = request.POST.get("cidade", "").strip()
                    faixa_etaria = request.POST.get("faixa_etaria", "").strip()
                    fingerprint = request.POST.get("fingerprint")
                    grupo = request.POST.get("grupo", "").strip()
                    genero = request.POST.get("genero", "").strip()
                    cor_raca = request.POST.get("cor_raca", "").strip()

                    if visitante_existente:
                        visitante_existente.pais = pais
                        visitante_existente.estado = estado
                        visitante_existente.cidade = cidade
                        visitante_existente.faixa_etaria = faixa_etaria
                        visitante_existente.grupo = grupo
                        visitante_existente.genero = genero
                        visitante_existente.cor_raca = cor_raca
                        visitante_existente.save()

                        messages.success(request, "Dados atualizados com sucesso!")
                        return redirect("index")
                    else:
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
                        
                        messages.success(request, "Seus dados foram enviados com sucesso!")
                        return redirect("index")
                
            except DatabaseError:
                messages.error(request, "Ocorreu um erro ao salvar no banco. Tente novamente.")

    return render(request, "cicero_experience/index.html", {
        "faixas_etarias_choices": faixas_etarias_choices,
        "grupo_": grupo_,
        "generos": generos,
        "cor_racas": cor_racas,
    })
