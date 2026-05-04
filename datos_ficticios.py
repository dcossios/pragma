"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Script entrypoint to generate mock data
"""

import os
import sys

from django.core.management import call_command


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pragma.settings")
    import django

    django.setup()
    clientes = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    facturas_por_cliente = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    call_command(
        "cargar_datos_ficticios",
        clientes=clientes,
        facturas_por_cliente=facturas_por_cliente,
    )


if __name__ == "__main__":
    main()
