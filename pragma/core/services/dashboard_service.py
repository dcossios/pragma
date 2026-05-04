"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Dashboard metrics aggregation service
"""

from decimal import Decimal

from django.db.models import Count

from pragma.core.models import DetallePago, Factura


def get_dashboard_metrics():
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

    return {
        "total_facturas_procesadas": total_facturas,
        "tasa_match_exitoso": tasa_match_exitoso,
        "validaciones_pendientes": validaciones_pendientes,
        "tiempo_ahorrado_horas": tiempo_ahorrado_horas,
        "inconsistencias_recientes": inconsistencias_recientes,
        "estado_breakdown": estado_breakdown,
    }
