"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: DetallePago model - payment matching results between invoice and bank certificate
"""

from django.db import models
from pragma.core.models.factura import Factura
from pragma.core.models.certificado_bancario import CertificadoBancario


class DetallePago(models.Model):
    """
    DetallePago model representing the result of matching
    an invoice with a bank certificate.
    Stores validation results and differences found.
    """

    ESTADO_MATCH_CHOICES = [
        ("match", "Coincide"),
        ("partial", "Coincide Parcialmente"),
        ("no_match", "No Coincide"),
    ]

    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name="detalles_pago",
        verbose_name="Factura",
        help_text="Factura asociada"
    )
    certificado = models.ForeignKey(
        CertificadoBancario,
        on_delete=models.CASCADE,
        related_name="detalles_pago",
        verbose_name="Certificado",
        help_text="Certificado bancario asociado"
    )
    estado_match = models.CharField(
        max_length=20,
        choices=ESTADO_MATCH_CHOICES,
        verbose_name="Estado del Match",
        help_text="Resultado de la comparación"
    )
    diferencias = models.TextField(
        blank=True,
        default="",
        verbose_name="Diferencias",
        help_text="Descripción de las diferencias encontradas"
    )
    resumen = models.TextField(
        verbose_name="Resumen",
        help_text="Resumen del análisis de pago"
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
    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Puntaje de Match",
        help_text="Puntaje de coincidencia (0-100)"
    )

    def __str__(self):
        return f"Detalle Pago: {self.factura.numero_factura} vs {self.certificado.numero_referencia}"

    class Meta:
        verbose_name = "Detalle Pago"
        verbose_name_plural = "Detalles de Pago"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["factura", "certificado"],
                name="unique_factura_certificado_match"
            )
        ]
