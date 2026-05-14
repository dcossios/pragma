"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-05-14
Description: Domain service for the invoice/payment workflow: upload pipeline,
finalization, certificate matching, search and client resolution.
"""

import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q

from pragma.core.models import Cliente, DetallePago, Factura
from pragma.core.services.comparador_pagos import (
    buscar_certificado_candidato,
    buscar_factura_candidata,
    crear_o_actualizar_detalle_pago,
)
from pragma.core.services.ocr_service import extract_invoice_data


def resolver_cliente(cliente, nit):
    """
    Resuelve la instancia de Cliente asociada a una factura o certificado.

    Args:
        cliente: Instancia de Cliente ya seleccionada, o None.
        nit (str | None): NIT con el que buscar el cliente si ``cliente`` es None.

    Returns:
        Cliente | None: El cliente recibido si no es None; en caso contrario, el
        primer Cliente cuyo ``nit`` coincida, o None si no existe ninguno.
    """
    if cliente:
        return cliente
    return Cliente.objects.filter(nit=nit).first()


def procesar_carga_factura(archivo, cliente):
    """
    Guarda el archivo subido en almacenamiento temporal y ejecuta la extracción OCR.

    Args:
        archivo: Archivo subido (``UploadedFile``) con la factura a procesar.
        cliente: Instancia de Cliente seleccionada en el formulario, o None.

    Returns:
        dict: Datos listos para guardar en ``request.session``, con las claves
        ``numero_factura``, ``monto`` (str|None), ``fecha`` (str|None),
        ``cliente_nit``, ``cliente_id`` (int|None), ``temp_path``, ``original_name``
        y ``errors`` (list[str]).

    Raises:
        OSError: Si falla la escritura en el almacenamiento temporal.
    """
    temp_name = f"temp/{uuid.uuid4()}_{archivo.name}"
    temp_path = default_storage.save(temp_name, ContentFile(archivo.read()))

    with default_storage.open(temp_path) as stored_file:
        ocr_result = extract_invoice_data(stored_file)

    monto = ocr_result.get("monto")
    fecha = ocr_result.get("fecha")
    return {
        "numero_factura": ocr_result.get("numero_factura"),
        "monto": str(monto) if monto else None,
        "fecha": str(fecha) if fecha else None,
        "cliente_nit": ocr_result.get("cliente_nit"),
        "cliente_id": cliente.id if cliente else None,
        "temp_path": temp_path,
        "original_name": archivo.name,
        "errors": ocr_result.get("errors", []),
    }


def finalizar_factura(factura, ocr_session_data, cliente_form):
    """
    Persiste una factura revisada y dispara el matching automático.

    Adjunta el archivo guardado en almacenamiento temporal, resuelve el cliente,
    guarda la factura, busca su certificado bancario candidato (creando o
    actualizando el DetallePago correspondiente) y elimina el archivo temporal.

    Args:
        factura: Instancia de Factura sin guardar (``form.save(commit=False)``).
        ocr_session_data (dict): Datos producidos por ``procesar_carga_factura``,
            con al menos ``temp_path`` y ``original_name``.
        cliente_form: Instancia de Cliente seleccionada en el formulario, o None.

    Returns:
        Factura: La factura ya persistida.

    Raises:
        django.db.DatabaseError: Si falla la escritura en la base de datos.
    """
    temp_path = ocr_session_data["temp_path"]
    if default_storage.exists(temp_path):
        with default_storage.open(temp_path) as stored_file:
            factura.archivo.save(
                ocr_session_data["original_name"], stored_file, save=False
            )

    factura.ocr_data = ocr_session_data
    factura.cliente = resolver_cliente(cliente_form, factura.cliente_nit)
    factura.save()

    certificado_candidato = buscar_certificado_candidato(factura)
    if certificado_candidato:
        crear_o_actualizar_detalle_pago(factura, certificado_candidato)

    if default_storage.exists(temp_path):
        default_storage.delete(temp_path)

    return factura


def finalizar_certificado(certificado, cliente_form):
    """
    Persiste un certificado bancario y dispara el matching automático.

    Resuelve el cliente, sincroniza el NIT a partir del cliente cuando falta,
    guarda el certificado y busca su factura candidata, creando o actualizando el
    DetallePago correspondiente.

    Args:
        certificado: Instancia de CertificadoBancario sin guardar
            (``form.save(commit=False)``).
        cliente_form: Instancia de Cliente seleccionada en el formulario, o None.

    Returns:
        Factura | None: La factura con la que se hizo el match, o None si no se
        encontró ninguna factura candidata.

    Raises:
        django.db.DatabaseError: Si falla la escritura en la base de datos.
    """
    certificado.cliente = resolver_cliente(cliente_form, certificado.cliente_nit)
    if certificado.cliente and not certificado.cliente_nit:
        certificado.cliente_nit = certificado.cliente.nit
    certificado.save()

    factura_candidata = buscar_factura_candidata(certificado)
    if factura_candidata:
        crear_o_actualizar_detalle_pago(factura_candidata, certificado)
    return factura_candidata


def buscar_facturas(search_query):
    """
    Devuelve las facturas, opcionalmente filtradas por un término de búsqueda.

    Args:
        search_query (str): Término a buscar en el número de factura, el NIT o el
            nombre del cliente. Si está vacío, se devuelven todas las facturas.

    Returns:
        QuerySet[Factura]: Facturas con ``cliente`` precargado vía ``select_related``.
    """
    facturas = Factura.objects.select_related("cliente").all()
    if search_query:
        facturas = facturas.filter(
            Q(numero_factura__icontains=search_query)
            | Q(cliente_nit__icontains=search_query)
            | Q(cliente__nombre__icontains=search_query)
        )
    return facturas


def buscar_pagos(estado):
    """
    Devuelve los detalles de pago, opcionalmente filtrados por estado de match.

    Args:
        estado (str): Estado de match por el que filtrar ("match", "partial",
            "no_match"). Si está vacío, se devuelven todos los detalles de pago.

    Returns:
        QuerySet[DetallePago]: Detalles de pago con ``factura`` y ``certificado``
        precargados vía ``select_related``.
    """
    detalles_pago = DetallePago.objects.select_related("factura", "certificado").all()
    if estado:
        detalles_pago = detalles_pago.filter(estado_match=estado)
    return detalles_pago
