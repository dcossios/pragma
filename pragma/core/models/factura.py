"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Factura model - invoice with OCR extracted data
"""

from django.db import models
from pragma.core.models.cliente import Cliente


class Factura(models.Model):
    """
    Factura model representing an invoice with OCR-extracted data.
    Stores invoice information extracted automatically from uploaded files.
    """

    numero_factura = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de Factura",
        help_text="Número único de la factura"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto",
        help_text="Monto total de la factura"
    )
    fecha = models.DateField(
        db_index=True,
        verbose_name="Fecha",
        help_text="Fecha de emisión de la factura"
    )
    cliente_nit = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="NIT Cliente",
        help_text="NIT del cliente que emite la factura"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="facturas",
        verbose_name="Cliente",
        help_text="Cliente relacionado a la factura"
    )
    archivo = models.FileField(
        upload_to="facturas/",
        verbose_name="Archivo",
        help_text="Archivo PDF o imagen de la factura"
    )
    ocr_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Datos OCR",
        help_text="Datos extraídos automáticamente mediante OCR"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
        help_text="Fecha y hora de creación del registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización",
        help_text="Fecha y hora de actualización del registro"
    )

    def __str__(self):
        return f"Factura {self.numero_factura} - {self.monto}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["-fecha", "-created_at"]
