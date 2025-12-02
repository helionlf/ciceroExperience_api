from __future__ import annotations

import csv
import math
from collections import defaultdict
from datetime import timedelta
from typing import Dict, List

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
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
    gender_totals_map = {item["key"]: item["total"] for item in gender_distribution}
    gender_pie = [
        {
            "key": "masculino",
            "label": "Masculino",
            "total": gender_totals_map.get("masculino", 0),
        },
        {
            "key": "feminino",
            "label": "Feminino",
            "total": gender_totals_map.get("feminino", 0),
        },
        {
            "key": "nao_informado",
            "label": "Nao informados/Outros",
            "total": sum(
                total
                for key, total in gender_totals_map.items()
                if key not in ("masculino", "feminino")
            ),
        },
    ]
    gender_pie_total = sum(piece["total"] for piece in gender_pie)
    for piece in gender_pie:
        if gender_pie_total:
            piece["percentage"] = round(piece["total"] / gender_pie_total * 100)
        else:
            piece["percentage"] = 0

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
    max_age_total = max((item["total"] for item in age_distribution), default=0)
    for item in age_distribution:
        if total_age_responses:
            item["percentage"] = round(item["total"] / total_age_responses * 100)
        else:
            item["percentage"] = 0

        if max_age_total and item["total"] > 0:
            scaled = int(item["total"] / max_age_total * 100)
            item["bar_width"] = max(15, scaled)
        else:
            item["bar_width"] = 0

    trend_series = _build_trend_series(date_range, filtered)
    trend_peak = max((point["total"] for point in trend_series), default=0)
    trend_ticks: List[int] = [0]
    if trend_peak:
        tick_step = max(1, math.ceil(trend_peak / 4))
        current = tick_step
        while current < trend_peak:
            trend_ticks.append(current)
            current += tick_step
        if trend_ticks[-1] != trend_peak:
            trend_ticks.append(trend_peak)
    trend_ticks = sorted(set(trend_ticks))
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

    filter_params = {
        "range": request.GET.get("range") or "",
        "since": request.GET.get("since") or date_range.start.strftime("%Y-%m-%d"),
        "until": request.GET.get("until") or date_range.end.strftime("%Y-%m-%d"),
    }

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
        "gender_pie": gender_pie,
        "gender_pie_total": gender_pie_total,
        "race_distribution": race_distribution,
        "city_rank": city_rank,
        "age_distribution": age_distribution,
        "trend_series": trend_series,
        "trend_peak": trend_peak,
        "trend_ticks": trend_ticks,
        "total_age_responses": total_age_responses,
        "recent_visitors": recent_visitors,
        "filter_options": FILTER_OPTIONS,
        "filter_params": filter_params,
    }

    return render(request, "dashboard/index.html", context)


@login_required
def export_dashboard_csv(request):
    date_range = resolve_date_range(
        range_key=request.GET.get("range"),
        since=request.GET.get("since"),
        until=request.GET.get("until"),
    )

    queryset = (
        Visitantes.objects.filter(data__range=(date_range.start, date_range.end))
        .order_by("data", "data_chekin")
    )

    filename = f"dashboard-visitas-{date_range.start:%Y%m%d}-{date_range.end:%Y%m%d}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "Data",
            "Data/Hora check-in",
            "Cidade",
            "Estado",
            "Pais",
            "Faixa etaria",
            "Genero",
            "Grupo",
            "Cor/Raca",
            "Fingerprint",
        ]
    )

    for visitante in queryset:
        writer.writerow(
            [
                visitante.data.isoformat() if visitante.data else "",
                visitante.data_chekin.strftime("%Y-%m-%d %H:%M:%S") if visitante.data_chekin else "",
                (visitante.cidade or "").strip(),
                (visitante.estado or "").strip(),
                (visitante.pais or "").strip(),
                visitante.get_faixa_etaria_display() or "",
                visitante.get_genero_display() or "",
                visitante.get_grupo_display() or "",
                visitante.get_cor_raca_display() or "",
                visitante.fingerprint,
            ]
        )

    return response
