"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: CertificadoBancario model - bank certificate for payment verification
"""

from django.db import models
from pragma.core.models.cliente import Cliente


class CertificadoBancario(models.Model):
    """
    CertificadoBancario model representing a bank certificate
    used for payment verification against invoices.
    """

    numero_referencia = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="Número de Referencia",
        help_text="Número único de referencia del certificado"
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Monto",
        help_text="Monto del certificado bancario"
    )
    fecha = models.DateField(
        db_index=True,
        verbose_name="Fecha",
        help_text="Fecha del certificado bancario"
    )
    cliente_nit = models.CharField(
        max_length=20,
        db_index=True,
        verbose_name="NIT Cliente",
        help_text="NIT del cliente asociado"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificados",
        verbose_name="Cliente",
        help_text="Cliente relacionado al certificado"
    )
    archivo = models.FileField(
        upload_to="certificados/",
        verbose_name="Archivo",
        help_text="Archivo PDF o imagen del certificado"
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
        return f"Certificado {self.numero_referencia} - {self.monto}"

    class Meta:
        verbose_name = "Certificado Bancario"
        verbose_name_plural = "Certificados Bancarios"
        ordering = ["-fecha", "-created_at"]
