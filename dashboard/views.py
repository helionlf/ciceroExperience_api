from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Dict, List

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from cicero_experience.models import Visitantes

from .data import FILTER_OPTIONS, DateRange, resolve_date_range

AGE_MIDPOINTS: Dict[str, int] = {
    "crianca": 9,
    "adolescente": 15,
    "jovem_adulto": 24,
    "adulto": 42,
    "idoso": 68,
}

GROUP_SUMMARIES: Dict[str, Dict[str, str]] = {
    "sim": {"highlight": "Compartilhada", "description": "Visita em grupo"},
    "nao": {"highlight": "Individual", "description": "Percurso pessoal"},
    "desconhecido": {"highlight": "Única", "description": "Local sagrado"},
    "default": {"highlight": "Única", "description": "Local sagrado"},
}

# MOVER AS FUNÇÕES AUXILIARES PARA CIMA, ANTES DA VIEW PRINCIPAL

def _build_age_distribution(queryset) -> List[Dict[str, str]]:
    counts = defaultdict(int)
    for item in queryset.values("faixa_etaria").annotate(total=Count("id")):
        counts[item["faixa_etaria"] or "nao_informado"] = item["total"]

    distribution = []
    for key, label in Visitantes.FAIXAS_ETARIAS:
        distribution.append(
            {
                "key": key,
                "label": label,
                "total": counts.get(key, 0),
            }
        )
    return distribution

def _build_trend_series(date_range: DateRange, queryset) -> List[Dict[str, object]]:
    counts_map = {
        item["data"]: item["total"]
        for item in queryset.values("data").annotate(total=Count("id")).order_by("data")
    }

    series = []
    for offset in range(date_range.days):
        current_date = date_range.start + timedelta(days=offset)
        total = counts_map.get(current_date, 0)
        series.append(
            {
                "date": current_date,
                "label": current_date.strftime("%d/%m"),
                "total": total,
            }
        )
    return series

def _build_group_distribution(queryset) -> List[Dict[str, str]]:
    counts = defaultdict(int)
    for item in queryset.values("grupo").annotate(total=Count("id")):
        counts[item["grupo"] or "desconhecido"] = item["total"]
    
    distribution = []
    for key, label in Visitantes.OPCOES_GRUPO:
        distribution.append({
            "key": key,
            "label": label,
            "total": counts.get(key, 0),
        })
    
    return sorted(distribution, key=lambda x: x["total"], reverse=True)

def _build_gender_distribution(queryset) -> List[Dict[str, str]]:
    counts = defaultdict(int)
    for item in queryset.values("genero").annotate(total=Count("id")):
        counts[item["genero"] or "nao_informado"] = item["total"]
    
    distribution = []
    for key, label in Visitantes.OPCOES_GENERO:
        distribution.append({
            "key": key,
            "label": label,
            "total": counts.get(key, 0),
        })
    
    return sorted(distribution, key=lambda x: x["total"], reverse=True)

def _build_race_distribution(queryset) -> List[Dict[str, str]]:
    counts = defaultdict(int)
    for item in queryset.values("cor_raca").annotate(total=Count("id")):
        counts[item["cor_raca"] or "nao_informado"] = item["total"]
    
    distribution = []
    for key, label in Visitantes.OPCOES_COR_RACA:
        distribution.append({
            "key": key,
            "label": label,
            "total": counts.get(key, 0),
        })
    
    return sorted(distribution, key=lambda x: x["total"], reverse=True)


@login_required
def index(request):
    date_range = resolve_date_range(
        range_key=request.GET.get("range"),
        since=request.GET.get("since"),
        until=request.GET.get("until"),
    )

    filtered = Visitantes.objects.filter(data__range=(date_range.start, date_range.end))

    total_visitors = filtered.count()
    states_count = (
        filtered.exclude(estado__isnull=True)
        .exclude(estado__exact="")
        .values("estado")
        .distinct()
        .count()
    )
    cities_count = (
        filtered.exclude(cidade__isnull=True)
        .exclude(cidade__exact="")
        .values("cidade")
        .distinct()
        .count()
    )

    age_queryset = (
        filtered.exclude(faixa_etaria__isnull=True)
        .exclude(faixa_etaria__exact="")
        .exclude(faixa_etaria="nao_informado")
        .values_list("faixa_etaria", flat=True)
    )
    age_values = [AGE_MIDPOINTS[choice] for choice in age_queryset if choice in AGE_MIDPOINTS]
    average_age = round(sum(age_values) / len(age_values)) if age_values else None

    # Nova métrica: Distribuição de Grupo
    group_distribution = _build_group_distribution(filtered)
    top_group_data = group_distribution[0] if group_distribution else None

    # Nova métrica: Distribuição de Gênero
    gender_distribution = _build_gender_distribution(filtered)
    top_gender_data = gender_distribution[0] if gender_distribution else None

    # Nova métrica: Distribuição de Cor/Raça
    race_distribution = _build_race_distribution(filtered)
    top_race_data = race_distribution[0] if race_distribution else None

    city_rank = list(
        filtered.exclude(cidade__isnull=True)
        .exclude(cidade__exact="")
        .values("cidade", "estado")
        .annotate(total=Count("id"))
        .order_by("-total", "cidade")[:5]
    )

    age_distribution = _build_age_distribution(filtered)
    total_age_responses = sum(item["total"] for item in age_distribution)
    for item in age_distribution:
        if total_age_responses:
            item["percentage"] = round(item["total"] / total_age_responses * 100)
        else:
            item["percentage"] = 0

    trend_series = _build_trend_series(date_range, filtered)
    trend_peak = max((point["total"] for point in trend_series), default=0)
    for point in trend_series:
        if trend_peak:
            point["height"] = max(6, int(point["total"] / trend_peak * 100))
        else:
            point["height"] = 6

    recent_visitors = []
    for visitor in filtered.order_by("-data_chekin")[:5]:
        city = (visitor.cidade or "").strip()
        state = (visitor.estado or "").strip()
        country = (visitor.pais or "").strip()
        location_parts = [part for part in (city, state) if part]
        location = " - ".join(location_parts) if location_parts else "Local não informado"
        initial_source = city or state or country or visitor.get_faixa_etaria_display() or "?"
        recent_visitors.append(
            {
                "location": location,
                "city": city or "Cidade não informada",
                "state": state,
                "country": country,
                "timestamp": visitor.data_chekin,
                "age_label": visitor.get_faixa_etaria_display(),
                "group_label": visitor.get_grupo_display(),
                "fingerprint": visitor.fingerprint,
                "initial": (initial_source[:1] or "?").upper(),
            }
        )

    context = {
        "date_range": date_range,
        "total_visitors": total_visitors,
        "cities_count": cities_count,
        "states_count": states_count,
        "average_age": average_age,
        "top_group_data": top_group_data,
        "top_gender_data": top_gender_data,
        "top_race_data": top_race_data,
        "group_distribution": group_distribution,
        "gender_distribution": gender_distribution,
        "race_distribution": race_distribution,
        "city_rank": city_rank,
        "age_distribution": age_distribution,
        "trend_series": trend_series,
        "trend_peak": trend_peak,
        "total_age_responses": total_age_responses,
        "recent_visitors": recent_visitors,
    }

    return render(request, "dashboard/index.html", context)