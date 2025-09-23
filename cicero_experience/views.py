from django.shortcuts import render
from django.shortcuts import redirect
from django.db import DatabaseError

from .models import Visitantes


def index(request):
    error_message = None

    if request.method == "POST":
        pais = request.POST.get("pais", "").strip()
        estado = request.POST.get("estado", "").strip()
        cidade = request.POST.get("cidade", "").strip()
        transporte = request.POST.get("transporte", "").strip()
        idade_str = request.POST.get("idade", "").strip()
        fingerprint = request.POST.get("fingerprint")

        if not fingerprint:
            error_message = "Não foi possível identificar o visitante."
        else:

            try:
                idade = int(idade_str)
                if idade <= 0 or idade > 150:
                    error_message = "Idade inválida."
                else:
                    try:
                        Visitantes.objects.create(
                            fingerprint=fingerprint,
                            pais=pais,
                            estado=estado,
                            cidade=cidade,
                            transporte=transporte,
                            idade=idade
                        )
                        return redirect("index")
                    except DatabaseError:
                        error_message = "Ocorreu um erro ao salvar no banco. Tente novamente."
                        print("aaaaaaaaaaaa", DatabaseError)
            except ValueError:
                error_message = "Idade inválida. Digite apenas números."

    visitantes_list = Visitantes.objects.order_by("-data_chekin")[:5]
    return render(request, "cicero_experience/index.html", {
        "visitantes_list": visitantes_list,
        "error_message": error_message
    })
