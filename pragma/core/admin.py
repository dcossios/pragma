"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Django admin registrations for core models
"""

from django.contrib import admin

from pragma.core.models import (
    CertificadoBancario,
    Cliente,
    DetallePago,
    Factura,
    Usuario,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nit", "nombre", "contacto", "created_at")
    search_fields = ("nit", "nombre", "contacto")
    ordering = ("nombre",)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ("numero_factura", "monto", "fecha", "cliente_nit", "created_at")
    search_fields = ("numero_factura", "cliente_nit")
    list_filter = ("fecha", "created_at")
    autocomplete_fields = ("cliente",)


@admin.register(CertificadoBancario)
class CertificadoBancarioAdmin(admin.ModelAdmin):
    list_display = ("numero_referencia", "monto", "fecha", "cliente_nit", "created_at")
    search_fields = ("numero_referencia", "cliente_nit")
    list_filter = ("fecha", "created_at")
    autocomplete_fields = ("cliente",)


@admin.register(DetallePago)
class DetallePagoAdmin(admin.ModelAdmin):
    list_display = ("factura", "certificado", "estado_match", "match_score", "created_at")
    search_fields = ("factura__numero_factura", "certificado__numero_referencia")
    list_filter = ("estado_match", "created_at")
    autocomplete_fields = ("factura", "certificado")


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "created_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("rol", "created_at")
