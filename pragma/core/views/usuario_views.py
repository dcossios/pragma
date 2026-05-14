"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: User-facing views including invoice upload
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from pragma.core.forms import FacturaEditForm, FacturaUploadForm
from pragma.core.models import DetallePago
from pragma.core.services.dashboard_service import get_dashboard_metrics
from pragma.core.services.export_service import exportar_excel, exportar_pdf
from pragma.core.services.factura_service import (
    buscar_facturas,
    buscar_pagos,
    finalizar_factura,
    procesar_carga_factura,
)


@login_required
def dashboard(request):
    metrics = get_dashboard_metrics()
    return render(request, "usuario/dashboard.html", {"metrics": metrics})


@login_required
def consulta_facturas(request):
    search_query = request.GET.get("q", "").strip()
    facturas = buscar_facturas(search_query)
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
            request.session["ocr_factura_data"] = procesar_carga_factura(
                form.cleaned_data["archivo"],
                form.cleaned_data["cliente"],
            )
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
            finalizar_factura(factura, data, form.cleaned_data.get("cliente"))
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
    detalles_pago = buscar_pagos(estado)
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
    detalles_pago = buscar_pagos("")
    output = exportar_excel(detalles_pago)
    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )
    response["Content-Disposition"] = 'attachment; filename="reporte_pagos.xlsx"'
    return response
