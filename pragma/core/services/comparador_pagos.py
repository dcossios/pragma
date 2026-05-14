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
    """
    Compara una factura con un certificado bancario y calcula un puntaje de coincidencia.

    El puntaje parte de 100.00 y se penaliza por cada inconsistencia detectada:
    monto distinto (-40), NIT distinto (-30), diferencia de fechas mayor a 2 días
    (-30) o diferencia de fechas de 1 a 2 días (-10). El puntaje nunca baja de 0.00.

    Args:
        factura_data: Objeto Factura (o equivalente) con los atributos ``monto``
            (Decimal), ``cliente_nit`` (str) y ``fecha`` (date).
        certificado_data: Objeto CertificadoBancario (o equivalente) con los mismos
            atributos ``monto``, ``cliente_nit`` y ``fecha``.

    Returns:
        dict: Diccionario con las claves:
            - ``estado_match`` (str): "match", "partial" o "no_match".
            - ``diferencias`` (list[str]): Descripción de cada inconsistencia.
            - ``match_score`` (Decimal): Puntaje final entre 0.00 y 100.00.
            - ``resumen`` (str): Resumen legible generado por ``generar_resumen_pagos``.

    Raises:
        AttributeError: Si alguno de los objetos no expone ``monto``,
            ``cliente_nit`` o ``fecha``.
        TypeError: Si los atributos tienen tipos incompatibles para las operaciones
            de comparación (por ejemplo, ``fecha`` que no sea ``date``).
    """
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
    """
    Genera un resumen legible del resultado de una comparación de pagos.

    Args:
        estado_match (str): Estado de la comparación: "match", "partial" o
            cualquier otro valor (tratado como "no_match").
        diferencias (list[str], optional): Lista de inconsistencias detectadas.
            Solo se incluye en el resumen para estados "partial" y "no_match".
            Por defecto None.
        match_score (Decimal, optional): Puntaje de coincidencia, mostrado en el
            resumen para estados "partial" y "no_match". Por defecto None.

    Returns:
        str: Texto descriptivo del resultado de la comparación.
    """
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
    """
    Compara una factura con un certificado y persiste el resultado en DetallePago.

    Ejecuta ``comparar_pagos`` y crea o actualiza (``update_or_create``) el registro
    de DetallePago asociado al par factura/certificado con el estado, las
    diferencias, el resumen y el puntaje obtenidos.

    Args:
        factura: Instancia de Factura a comparar y vincular.
        certificado: Instancia de CertificadoBancario a comparar y vincular.

    Returns:
        DetallePago: La instancia creada o actualizada.

    Raises:
        AttributeError: Si ``factura`` o ``certificado`` no exponen los atributos
            requeridos por ``comparar_pagos``.
        django.db.DatabaseError: Si falla la operación de escritura en la base de datos.
    """
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
    """
    Busca la mejor factura candidata para un certificado bancario dado.

    Filtra las facturas que comparten el ``cliente_nit`` del certificado y elige la
    que minimiza, en orden de prioridad, la diferencia de monto y la diferencia de
    días respecto al certificado.

    Args:
        certificado: Instancia de CertificadoBancario con los atributos
            ``cliente_nit``, ``monto`` y ``fecha``.

    Returns:
        Factura | None: La factura con menor diferencia de monto y fecha, o None si
        ningún registro comparte el NIT del certificado.

    Raises:
        AttributeError: Si ``certificado`` no expone ``cliente_nit``, ``monto`` o
            ``fecha``.
    """
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
    Busca el mejor certificado bancario candidato para una factura dada.

    Filtra los certificados que comparten el ``cliente_nit`` de la factura y elige el
    que minimiza, en orden de prioridad, la diferencia de monto y la diferencia de
    días respecto a la factura.

    Args:
        factura: Instancia de Factura con los atributos ``cliente_nit``, ``monto`` y
            ``fecha``.

    Returns:
        CertificadoBancario | None: El certificado con menor diferencia de monto y
        fecha, o None si ningún registro comparte el NIT de la factura.

    Raises:
        AttributeError: Si ``factura`` no expone ``cliente_nit``, ``monto`` o
            ``fecha``.
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
