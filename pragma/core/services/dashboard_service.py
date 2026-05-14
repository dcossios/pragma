"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Dashboard metrics aggregation service
"""

from decimal import Decimal

from django.db.models import Count, Q

from pragma.core.models import CertificadoBancario, DetallePago, Factura


def get_dashboard_metrics():
    """
    Calcula las métricas agregadas que alimentan el dashboard.

    Consulta los modelos Factura y DetallePago para obtener totales, tasas de
    coincidencia, validaciones pendientes, tiempo estimado ahorrado, las
    inconsistencias más recientes y el desglose por estado de match.

    Returns:
        dict: Diccionario con las claves:
            - ``total_facturas_procesadas`` (int): Total de facturas registradas.
            - ``tasa_match_exitoso`` (float): Porcentaje de DetallePago con estado
              "match" sobre el total de comparaciones.
            - ``validaciones_pendientes`` (int): Facturas sin ningún DetallePago.
            - ``tiempo_ahorrado_horas`` (Decimal): Horas estimadas ahorradas frente
              al proceso manual.
            - ``inconsistencias_recientes`` (QuerySet): Hasta 5 DetallePago con
              estado distinto de "match", ordenados por fecha descendente.
            - ``estado_breakdown`` (QuerySet): Conteo de DetallePago agrupado por
              ``estado_match``.
            - ``tasa_match_sobre_total`` (float): Porcentaje de DetallePago con
              estado "match" sobre el total de facturas procesadas.
            - ``distribucion_score`` (dict): Conteo de DetallePago por rango de
              ``match_score`` con las claves ``rango_0_49``, ``rango_50_69``,
              ``rango_70_89`` y ``rango_90_100``.
            - ``facturas_sin_certificado_candidato`` (int): Facturas cuyo
              ``cliente_nit`` no aparece en ningún CertificadoBancario.

    Raises:
        django.db.DatabaseError: Si falla alguna de las consultas a la base de datos.
    """
    total_facturas = Factura.objects.count()
    total_matches = DetallePago.objects.filter(estado_match="match").count()
    total_comparaciones = DetallePago.objects.count()

    if total_comparaciones > 0:
        tasa_match_exitoso = round((total_matches / total_comparaciones) * 100, 2)
    else:
        tasa_match_exitoso = 0

    facturas_con_validacion = DetallePago.objects.values("factura").distinct().count()
    validaciones_pendientes = max(total_facturas - facturas_con_validacion, 0)

    # Estimación: proceso manual ~3h por cliente/factura, automatizado ~0.25h.
    tiempo_ahorrado_horas = Decimal(max(total_facturas * 2.75, 0)).quantize(Decimal("0.01"))

    inconsistencias_recientes = (
        DetallePago.objects.exclude(estado_match="match")
        .select_related("factura", "certificado")
        .order_by("-created_at")[:5]
    )

    estado_breakdown = (
        DetallePago.objects.values("estado_match")
        .annotate(total=Count("id"))
        .order_by("estado_match")
    )

    if total_facturas > 0:
        tasa_match_sobre_total = round((total_matches / total_facturas) * 100, 2)
    else:
        tasa_match_sobre_total = 0

    distribucion_score = DetallePago.objects.aggregate(
        rango_0_49=Count("id", filter=Q(match_score__lt=50)),
        rango_50_69=Count("id", filter=Q(match_score__gte=50, match_score__lt=70)),
        rango_70_89=Count("id", filter=Q(match_score__gte=70, match_score__lt=90)),
        rango_90_100=Count("id", filter=Q(match_score__gte=90)),
    )

    nits_con_certificado = CertificadoBancario.objects.values_list(
        "cliente_nit", flat=True
    )
    facturas_sin_certificado_candidato = Factura.objects.exclude(
        cliente_nit__in=nits_con_certificado
    ).count()

    return {
        "total_facturas_procesadas": total_facturas,
        "tasa_match_exitoso": tasa_match_exitoso,
        "validaciones_pendientes": validaciones_pendientes,
        "tiempo_ahorrado_horas": tiempo_ahorrado_horas,
        "inconsistencias_recientes": inconsistencias_recientes,
        "estado_breakdown": estado_breakdown,
        "tasa_match_sobre_total": tasa_match_sobre_total,
        "distribucion_score": distribucion_score,
        "facturas_sin_certificado_candidato": facturas_sin_certificado_candidato,
    }
