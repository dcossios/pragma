"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Smart matching service between invoices and bank certificates
"""

from datetime import timedelta
from decimal import Decimal

from pragma.core.models import DetallePago, Factura, CertificadoBancario


def _format_difference(field, factura_value, certificado_value, message):
    return f"{field}: factura={factura_value} | certificado={certificado_value}. {message}"


def comparar_pagos(factura_data, certificado_data):
    differences = []
    score = Decimal("100.00")

    if factura_data.monto != certificado_data.monto:
        score -= Decimal("40.00")
        differences.append(
            _format_difference(
                "monto",
                factura_data.monto,
                certificado_data.monto,
                "Los montos no coinciden.",
            )
        )

    if factura_data.cliente_nit != certificado_data.cliente_nit:
        score -= Decimal("30.00")
        differences.append(
            _format_difference(
                "cliente_nit",
                factura_data.cliente_nit,
                certificado_data.cliente_nit,
                "El NIT no coincide.",
            )
        )

    date_delta = abs(factura_data.fecha - certificado_data.fecha)
    if date_delta > timedelta(days=2):
        score -= Decimal("30.00")
        differences.append(
            _format_difference(
                "fecha",
                factura_data.fecha,
                certificado_data.fecha,
                "La diferencia de fechas supera 2 días.",
            )
        )
    elif date_delta > timedelta(days=0):
        score -= Decimal("10.00")
        differences.append(
            _format_difference(
                "fecha",
                factura_data.fecha,
                certificado_data.fecha,
                "Las fechas no son idénticas.",
            )
        )

    if score < 0:
        score = Decimal("0.00")

    if score >= Decimal("90.00") and not differences:
        status = "match"
    elif score >= Decimal("50.00"):
        status = "partial"
    else:
        status = "no_match"

    return {
        "estado_match": status,
        "diferencias": differences,
        "match_score": score,
        "resumen": generar_resumen_pagos(status, differences, score),
    }


def generar_resumen_pagos(estado_match, diferencias=None, match_score=None):
    if estado_match == "match":
        return "La factura y el certificado bancario coinciden completamente."
    if estado_match == "partial":
        return (
            f"Se detectó coincidencia parcial ({match_score}%). "
            f"Diferencias: {' | '.join(diferencias or [])}"
        )
    return (
        f"No hay coincidencia suficiente ({match_score}%). "
        f"Inconsistencias: {' | '.join(diferencias or [])}"
    )


def crear_o_actualizar_detalle_pago(factura, certificado):
    comparison = comparar_pagos(factura, certificado)
    detalle_pago, _ = DetallePago.objects.update_or_create(
        factura=factura,
        certificado=certificado,
        defaults={
            "estado_match": comparison["estado_match"],
            "diferencias": "\n".join(comparison["diferencias"]),
            "resumen": comparison["resumen"],
            "match_score": comparison["match_score"],
        },
    )
    return detalle_pago


def buscar_factura_candidata(certificado):
    candidates = Factura.objects.filter(cliente_nit=certificado.cliente_nit).order_by("-fecha")
    best_invoice = None
    best_score = None
    for candidate in candidates:
        amount_diff = abs(candidate.monto - certificado.monto)
        days_diff = abs((candidate.fecha - certificado.fecha).days)
        ranking = (amount_diff, days_diff)
        if best_score is None or ranking < best_score:
            best_score = ranking
            best_invoice = candidate
    return best_invoice


def buscar_certificado_candidato(factura):
    """
    Looks for the best bank certificate candidate for a given invoice.
    """
    candidates = CertificadoBancario.objects.filter(cliente_nit=factura.cliente_nit).order_by("-fecha")
    best_cert = None
    best_score = None
    for candidate in candidates:
        amount_diff = abs(candidate.monto - factura.monto)
        days_diff = abs((candidate.fecha - factura.fecha).days)
        ranking = (amount_diff, days_diff)
        if best_score is None or ranking < best_score:
            best_score = ranking
            best_cert = candidate
    return best_cert
