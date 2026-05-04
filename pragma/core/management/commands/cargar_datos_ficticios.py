"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Management command to generate deterministic mock data
"""

from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from pragma.core.models import CertificadoBancario, Cliente, Factura
from pragma.core.services.comparador_pagos import crear_o_actualizar_detalle_pago


def _dummy_pdf_bytes(title):
    content = (
        b"%PDF-1.1\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] >> endobj\n"
        b"trailer << /Root 1 0 R >>\n%%EOF"
    )
    return BytesIO(content + f"\n% {title}".encode("utf-8")).getvalue()


class Command(BaseCommand):
    help = "Carga datos ficticios para facturas, certificados y detalles de pago."

    def add_arguments(self, parser):
        parser.add_argument("--clientes", type=int, default=5)
        parser.add_argument("--facturas-por-cliente", type=int, default=3)

    def handle(self, *args, **options):
        clients_count = options["clientes"]
        invoices_per_client = options["facturas_por_cliente"]
        base_date = date(2026, 3, 1)

        for client_index in range(1, clients_count + 1):
            nit = f"1000{client_index:03d}-1"
            cliente, _ = Cliente.objects.get_or_create(
                nit=nit,
                defaults={
                    "nombre": f"Cliente {client_index}",
                    "contacto": f"cliente{client_index}@example.com",
                },
            )

            for invoice_index in range(1, invoices_per_client + 1):
                invoice_number = f"FAC-{client_index:03d}-{invoice_index:03d}"
                ref_number = f"REF-{client_index:03d}-{invoice_index:03d}"
                amount = Decimal("750.00") + Decimal(client_index * invoice_index)
                invoice_date = base_date + timedelta(days=invoice_index)

                factura, _ = Factura.objects.get_or_create(
                    numero_factura=invoice_number,
                    defaults={
                        "monto": amount,
                        "fecha": invoice_date,
                        "cliente_nit": nit,
                        "cliente": cliente,
                        "archivo": ContentFile(
                            _dummy_pdf_bytes(invoice_number),
                            name=f"factura_{invoice_number}.pdf",
                        ),
                        "ocr_data": {
                            "numero_factura": invoice_number,
                            "cliente_nit": nit,
                            "monto": str(amount),
                            "fecha": str(invoice_date),
                            "errors": [],
                            "raw_text": "mock seed data",
                        },
                    },
                )

                certificate_amount = amount if invoice_index % 2 else amount + Decimal("25.00")
                certificado, _ = CertificadoBancario.objects.get_or_create(
                    numero_referencia=ref_number,
                    defaults={
                        "monto": certificate_amount,
                        "fecha": invoice_date,
                        "cliente_nit": nit,
                        "cliente": cliente,
                        "archivo": ContentFile(
                            _dummy_pdf_bytes(ref_number),
                            name=f"certificado_{ref_number}.pdf",
                        ),
                    },
                )

                crear_o_actualizar_detalle_pago(factura, certificado)

        self.stdout.write(self.style.SUCCESS("Datos ficticios cargados correctamente."))
