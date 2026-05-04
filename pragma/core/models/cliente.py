"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Cliente model - represents a client/taxpayer entity
"""

from django.db import models


class Cliente(models.Model):
    """
    Cliente entity representing a taxpayer or company
    that issues invoices and has bank certificates.
    """

    nit = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="NIT",
        help_text="Número de Identificación Tributaria"
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre completo del cliente"
    )
    contacto = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Contacto",
        help_text="Información de contacto (email, teléfono)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )

    def __str__(self):
        return f"{self.nombre} ({self.nit})"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]
