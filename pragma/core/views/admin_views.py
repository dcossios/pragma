"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Admin-panel views for CRUD and matching operations
"""

import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from pragma.core.forms import (
    CertificadoBancarioForm,
    FacturaEditForm,
    FacturaUploadForm,
    UsuarioCreationWithRoleForm,
    UsuarioRoleUpdateForm,
)
from pragma.core.models import CertificadoBancario, Cliente, Factura, Usuario
from pragma.core.permissions import ensure_admin_or_raise
from pragma.core.services.comparador_pagos import (
    buscar_certificado_candidato,
    buscar_factura_candidata,
    crear_o_actualizar_detalle_pago,
)
from pragma.core.services.ocr_service import extract_invoice_data


def _resolver_cliente(cliente, nit):
    if cliente:
        return cliente
    return Cliente.objects.filter(nit=nit).first()


@login_required
def admin_home(request):
    ensure_admin_or_raise(request)
    return redirect("admin_panel:admin_facturas")


@login_required
def admin_facturas(request):
    ensure_admin_or_raise(request)

    if request.method == "POST":
        form = FacturaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            cliente = form.cleaned_data["cliente"]

            temp_name = f"temp/{uuid.uuid4()}_{archivo.name}"
            path = default_storage.save(temp_name, ContentFile(archivo.read()))

            with default_storage.open(path) as f:
                ocr_result = extract_invoice_data(f)

            request.session["ocr_factura_data_admin"] = {
                "numero_factura": ocr_result.get("numero_factura"),
                "monto": str(ocr_result.get("monto")) if ocr_result.get("monto") else None,
                "fecha": str(ocr_result.get("fecha")) if ocr_result.get("fecha") else None,
                "cliente_nit": ocr_result.get("cliente_nit"),
                "cliente_id": cliente.id if cliente else None,
                "temp_path": path,
                "original_name": archivo.name,
                "errors": ocr_result.get("errors", []),
            }
            return redirect("admin_panel:revisar_factura_admin")
    else:
        form = FacturaUploadForm()

    facturas = Factura.objects.select_related("cliente").all()
    return render(
        request,
        "admin_panel/facturas.html",
        {
            "form": form,
            "facturas": facturas,
        },
    )


@login_required
def revisar_factura_admin(request):
    ensure_admin_or_raise(request)
    data = request.session.get("ocr_factura_data_admin")
    if not data:
        messages.error(request, "No hay datos de factura para revisar.")
        return redirect("admin_panel:admin_facturas")

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
            del request.session["ocr_factura_data_admin"]

            messages.success(request, f"Factura {factura.numero_factura} guardada correctamente.")
            return redirect("admin_panel:admin_facturas")
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

    return render(request, "admin_panel/revisar_factura.html", {"form": form, "ocr_errors": data.get("errors")})


@login_required
def editar_factura(request, factura_id):
    ensure_admin_or_raise(request)
    factura = get_object_or_404(Factura, pk=factura_id)
    if request.method == "POST":
        form = FacturaEditForm(request.POST, request.FILES, instance=factura)
        if form.is_valid():
            form.save()
            messages.success(request, "Factura actualizada correctamente.")
            return redirect("admin_panel:admin_facturas")
    else:
        form = FacturaEditForm(instance=factura)
    return render(
        request,
        "admin_panel/editar_factura.html",
        {"form": form, "factura": factura},
    )


@login_required
def eliminar_factura(request, factura_id):
    ensure_admin_or_raise(request)
    factura = get_object_or_404(Factura, pk=factura_id)
    if request.method == "POST":
        factura.delete()
        messages.success(request, "Factura eliminada correctamente.")
    return redirect("admin_panel:admin_facturas")


@login_required
def admin_certificados(request):
    ensure_admin_or_raise(request)

    if request.method == "POST":
        form = CertificadoBancarioForm(request.POST, request.FILES)
        if form.is_valid():
            certificado = form.save(commit=False)
            certificado.cliente = _resolver_cliente(
                form.cleaned_data.get("cliente"),
                certificado.cliente_nit,
            )
            if certificado.cliente and not certificado.cliente_nit:
                certificado.cliente_nit = certificado.cliente.nit
            certificado.save()

            factura_candidata = buscar_factura_candidata(certificado)
            if factura_candidata:
                crear_o_actualizar_detalle_pago(factura_candidata, certificado)
                messages.success(
                    request,
                    "Certificado creado y comparación automática ejecutada.",
                )
            else:
                messages.warning(
                    request,
                    "Certificado creado, pero no se encontró factura para comparar.",
                )
            return HttpResponseRedirect(reverse("admin_panel:admin_certificados"))
    else:
        form = CertificadoBancarioForm()

    certificados = CertificadoBancario.objects.select_related("cliente").all()
    return render(
        request,
        "admin_panel/certificados.html",
        {
            "form": form,
            "certificados": certificados,
        },
    )


@login_required
def editar_certificado(request, certificado_id):
    ensure_admin_or_raise(request)
    certificado = get_object_or_404(CertificadoBancario, pk=certificado_id)
    if request.method == "POST":
        form = CertificadoBancarioForm(request.POST, request.FILES, instance=certificado)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificado actualizado correctamente.")
            return redirect("admin_panel:admin_certificados")
    else:
        form = CertificadoBancarioForm(instance=certificado)
    return render(
        request,
        "admin_panel/editar_certificado.html",
        {"form": form, "certificado": certificado},
    )


@login_required
def eliminar_certificado(request, certificado_id):
    ensure_admin_or_raise(request)
    certificado = get_object_or_404(CertificadoBancario, pk=certificado_id)
    if request.method == "POST":
        certificado.delete()
        messages.success(request, "Certificado eliminado correctamente.")
    return redirect("admin_panel:admin_certificados")


@login_required
def admin_usuarios(request):
    ensure_admin_or_raise(request)

    if request.method == "POST":
        form = UsuarioCreationWithRoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado correctamente.")
            return HttpResponseRedirect(reverse("admin_panel:admin_usuarios"))
    else:
        form = UsuarioCreationWithRoleForm()

    perfiles = Usuario.objects.select_related("user").all()
    return render(
        request,
        "admin_panel/usuarios.html",
        {
            "form": form,
            "perfiles": perfiles,
        },
    )


@login_required
def editar_usuario(request, usuario_id):
    ensure_admin_or_raise(request)
    perfil = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == "POST":
        form = UsuarioRoleUpdateForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Rol actualizado correctamente.")
            return redirect("admin_panel:admin_usuarios")
    else:
        form = UsuarioRoleUpdateForm(instance=perfil)
    return render(
        request,
        "admin_panel/editar_usuario.html",
        {
            "form": form,
            "perfil": perfil,
        },
    )


@login_required
def eliminar_usuario(request, usuario_id):
    ensure_admin_or_raise(request)
    perfil = get_object_or_404(Usuario.objects.select_related("user"), pk=usuario_id)
    if request.method == "POST":
        if perfil.user == request.user:
            messages.error(request, "No puedes eliminar tu propio usuario.")
        else:
            user_id = perfil.user_id
            perfil.delete()
            User.objects.filter(id=user_id).delete()
            messages.success(request, "Usuario eliminado correctamente.")
    return redirect("admin_panel:admin_usuarios")