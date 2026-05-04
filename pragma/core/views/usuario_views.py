"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: User-facing views including invoice upload
"""

import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from pragma.core.forms import FacturaEditForm, FacturaUploadForm
from pragma.core.models import Cliente, DetallePago, Factura
from pragma.core.services.comparador_pagos import (
    buscar_certificado_candidato,
    crear_o_actualizar_detalle_pago,
)
from pragma.core.services.dashboard_service import get_dashboard_metrics
from pragma.core.services.export_service import exportar_excel, exportar_pdf
from pragma.core.services.ocr_service import extract_invoice_data


def _resolver_cliente(cliente, nit):
    if cliente:
        return cliente
    return Cliente.objects.filter(nit=nit).first()


@login_required
def dashboard(request):
    metrics = get_dashboard_metrics()
    return render(request, "usuario/dashboard.html", {"metrics": metrics})


@login_required
def consulta_facturas(request):
    search_query = request.GET.get("q", "").strip()
    facturas = Factura.objects.select_related("cliente").all()
    if search_query:
        facturas = facturas.filter(
            Q(numero_factura__icontains=search_query)
            | Q(cliente_nit__icontains=search_query)
            | Q(cliente__nombre__icontains=search_query)
        )
    return render(
        request,
        "usuario/facturas.html",
        {
            "facturas": facturas,
            "search_query": search_query,
        },
    )


@login_required
def cargar_factura(request):
    if request.method == "POST":
        form = FacturaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            cliente = form.cleaned_data["cliente"]

            temp_name = f"temp/{uuid.uuid4()}_{archivo.name}"
            path = default_storage.save(temp_name, ContentFile(archivo.read()))

            with default_storage.open(path) as f:
                ocr_result = extract_invoice_data(f)

            request.session["ocr_factura_data"] = {
                "numero_factura": ocr_result.get("numero_factura"),
                "monto": str(ocr_result.get("monto")) if ocr_result.get("monto") else None,
                "fecha": str(ocr_result.get("fecha")) if ocr_result.get("fecha") else None,
                "cliente_nit": ocr_result.get("cliente_nit"),
                "cliente_id": cliente.id if cliente else None,
                "temp_path": path,
                "original_name": archivo.name,
                "errors": ocr_result.get("errors", []),
            }
            return redirect("usuario:revisar_factura")
    else:
        form = FacturaUploadForm()

    return render(request, "usuario/cargar_factura.html", {"form": form})


@login_required
def revisar_factura(request):
    data = request.session.get("ocr_factura_data")
    if not data:
        messages.error(request, "No hay datos de factura para revisar.")
        return redirect("usuario:cargar_factura")

    if request.method == "POST":
        form = FacturaEditForm(request.POST)
        if form.is_valid():
            factura = form.save(commit=False)

            temp_path = data["temp_path"]
            if default_storage.exists(temp_path):
                with default_storage.open(temp_path) as f:
                    factura.archivo.save(data["original_name"], f, save=False)

            factura.ocr_data = data
            factura.cliente = _resolver_cliente(form.cleaned_data.get("cliente"), factura.cliente_nit)
            factura.save()

            certificado_candidato = buscar_certificado_candidato(factura)
            if certificado_candidato:
                crear_o_actualizar_detalle_pago(factura, certificado_candidato)

            default_storage.delete(temp_path)
            del request.session["ocr_factura_data"]

            messages.success(request, f"Factura {factura.numero_factura} guardada correctamente.")
            return redirect("usuario:consulta_facturas")
    else:
        initial = {
            "numero_factura": data.get("numero_factura"),
            "monto": data.get("monto"),
            "fecha": data.get("fecha"),
            "cliente_nit": data.get("cliente_nit"),
            "cliente": data.get("cliente_id"),
        }
        form = FacturaEditForm(initial=initial)
        if data.get("errors"):
            messages.warning(request, "El OCR tuvo dificultades: " + " | ".join(data["errors"]))

    return render(request, "usuario/revisar_factura.html", {"form": form, "ocr_errors": data.get("errors")})


@login_required
def consulta_pagos(request):
    estado = request.GET.get("estado", "").strip()
    detalles_pago = DetallePago.objects.select_related("factura", "certificado").all()
    if estado:
        detalles_pago = detalles_pago.filter(estado_match=estado)
    return render(
        request,
        "usuario/pagos.html",
        {
            "detalles_pago": detalles_pago,
            "estado": estado,
        },
    )


@login_required
def exportar_pago_pdf(request, pago_id):
    detalle_pago = get_object_or_404(
        DetallePago.objects.select_related("factura", "certificado"),
        pk=pago_id,
    )
    output = exportar_pdf(detalle_pago)
    response = HttpResponse(output.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="resumen_pago_{detalle_pago.id}.pdf"'
    )
    return response


@login_required
def exportar_pagos_excel(request):
    detalles_pago = DetallePago.objects.select_related("factura", "certificado").all()
    output = exportar_excel(detalles_pago)
    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = 'attachment; filename="reporte_pagos.xlsx"'
    return response