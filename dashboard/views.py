from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from cicero_experience.models import Visitantes
from django.db.models import Count 
import datetime

@login_required
def index(request):
    # 1. Defina o início e o fim do dia
    # Usando timezone.now().date() para pegar a data atual (sem hora)
    hoje = timezone.now().date()
    
    # Se você quiser usar o campo 'data' (que é DateField)
    contagem_visitantes_hoje = Visitantes.objects.filter(data=hoje).count()
    
    # OU, se você quiser garantir que está pegando tudo do dia de HOJE,
    # comparando com o campo data_chekin (que é DateTimeField)
    # OBS: Certifique-se que o timezone está configurado corretamente no seu settings.py!
    
    # Início do dia
    inicio_do_dia = timezone.make_aware(datetime.datetime.combine(hoje, datetime.time.min))
    # Fim do dia
    fim_do_dia = timezone.make_aware(datetime.datetime.combine(hoje, datetime.time.max))

    contagem_visitantes_hoje_dt = Visitantes.objects.filter(
        data_chekin__range=(inicio_do_dia, fim_do_dia)
    ).count()

    # Para o seu modelo, usar .filter(data=hoje).count() deve ser o suficiente e mais limpo.
    
    context = {
        'contagem_visitantes_hoje': contagem_visitantes_hoje,
        # Você pode adicionar outras estatísticas aqui...
    }
    
    return render(request, 'dashboard/index.html', context)