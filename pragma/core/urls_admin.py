"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Custom admin panel URL configuration
"""

from django.urls import path

from pragma.core.views import admin_views

app_name = "admin_panel"

urlpatterns = [
    path("", admin_views.admin_home, name="home"),
    path("facturas/", admin_views.admin_facturas, name="admin_facturas"),
    path("facturas/revisar/", admin_views.revisar_factura_admin, name="revisar_factura_admin"),
    path("facturas/<int:factura_id>/editar/", admin_views.editar_factura, name="editar_factura"),
    path("facturas/<int:factura_id>/eliminar/", admin_views.eliminar_factura, name="eliminar_factura"),
    path("certificados/", admin_views.admin_certificados, name="admin_certificados"),
    path(
        "certificados/<int:certificado_id>/editar/",
        admin_views.editar_certificado,
        name="editar_certificado",
    ),
    path(
        "certificados/<int:certificado_id>/eliminar/",
        admin_views.eliminar_certificado,
        name="eliminar_certificado",
    ),
    path("usuarios/", admin_views.admin_usuarios, name="admin_usuarios"),
    path("usuarios/<int:usuario_id>/editar/", admin_views.editar_usuario, name="editar_usuario"),
    path("usuarios/<int:usuario_id>/eliminar/", admin_views.eliminar_usuario, name="eliminar_usuario"),
]
