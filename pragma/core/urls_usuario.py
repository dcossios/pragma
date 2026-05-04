"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: User section URL configuration
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from pragma.core.views import usuario_views

app_name = "usuario"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="usuario/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", usuario_views.dashboard, name="dashboard"),
    path("facturas/", usuario_views.consulta_facturas, name="consulta_facturas"),
    path("facturas/cargar/", usuario_views.cargar_factura, name="cargar_factura"),
    path("facturas/revisar/", usuario_views.revisar_factura, name="revisar_factura"),
    path("pagos/", usuario_views.consulta_pagos, name="consulta_pagos"),
    path("pagos/export/excel/", usuario_views.exportar_pagos_excel, name="exportar_pagos_excel"),
    path("pagos/<int:pago_id>/export/pdf/", usuario_views.exportar_pago_pdf, name="exportar_pago_pdf"),
]
