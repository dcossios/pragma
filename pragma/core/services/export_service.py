"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Report export service for PDF and Excel outputs
"""

from io import BytesIO

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def exportar_pdf(detalle_pago):
    """
    Genera un reporte PDF con el resumen de verificación de un pago.

    Construye un documento A4 con los datos del detalle de pago (factura,
    certificado, estado, puntaje, resumen y diferencias), paginando automáticamente
    cuando el contenido excede la altura de la página.

    Args:
        detalle_pago: Instancia de DetallePago con las relaciones ``factura`` y
            ``certificado`` accesibles, y los campos ``estado_match``,
            ``match_score``, ``resumen`` y ``diferencias``.

    Returns:
        io.BytesIO: Buffer en memoria posicionado al inicio, con el PDF generado
        listo para ser servido o guardado.

    Raises:
        AttributeError: Si ``detalle_pago`` o sus relaciones no exponen los campos
            esperados.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y_position = height - 50

    lines = [
        "Resumen de Verificación de Pago",
        f"Factura: {detalle_pago.factura.numero_factura}",
        f"Certificado: {detalle_pago.certificado.numero_referencia}",
        f"Estado: {detalle_pago.estado_match}",
        f"Puntaje: {detalle_pago.match_score}",
        f"Resumen: {detalle_pago.resumen}",
    ]
    if detalle_pago.diferencias:
        lines.append("Diferencias:")
        lines.extend(detalle_pago.diferencias.split("\n"))

    for line in lines:
        if y_position < 40:
            pdf.showPage()
            y_position = height - 50
        pdf.drawString(50, y_position, str(line)[:120])
        y_position -= 20

    pdf.save()
    buffer.seek(0)
    return buffer


def exportar_excel(detalles_pago):
    """
    Genera un reporte Excel (.xlsx) con una fila por cada detalle de pago.

    Crea un libro con la hoja "Pagos", una fila de encabezados y una fila por
    elemento del iterable con los datos de la factura y el certificado asociados.

    Args:
        detalles_pago (Iterable): Iterable de instancias DetallePago, cada una con
            las relaciones ``factura`` y ``certificado`` accesibles y los campos
            ``estado_match`` y ``match_score``.

    Returns:
        io.BytesIO: Buffer en memoria posicionado al inicio, con el archivo Excel
        generado listo para ser servido o guardado.

    Raises:
        AttributeError: Si algún elemento o sus relaciones no exponen los campos
            esperados.
    """
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Pagos"

    worksheet.append(
        [
            "Factura",
            "Certificado",
            "Estado",
            "Puntaje",
            "Monto Factura",
            "Monto Certificado",
            "NIT Factura",
            "NIT Certificado",
        ]
    )

    for detalle in detalles_pago:
        worksheet.append(
            [
                detalle.factura.numero_factura,
                detalle.certificado.numero_referencia,
                detalle.estado_match,
                float(detalle.match_score),
                float(detalle.factura.monto),
                float(detalle.certificado.monto),
                detalle.factura.cliente_nit,
                detalle.certificado.cliente_nit,
            ]
        )

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
