#  Pragma - Django OCR Invoice Processing System

##  Context

### Problem

Accounting firms spend **2–4 hours per client** manually verifying payments by reviewing:

* Invoices
* Bank certificates
* Payment files

This process is:

* Slow
* Error-prone
* Highly dependent on human intervention

### Solution

Build a **Django web application** that:

* Automates OCR reading of invoices (PDF/PNG/JPG)
* Validates extracted data
* Compares it with bank certificates and payment records

 Expected result: **Reduce processing time to ~15 minutes**

### Target

* Small accounting firm (~6 people)
* Controlled initial environment

---

#  Implementation Plan

## Phase 1: Project Setup

1. Initialize Django project with PostgreSQL database
2. Create Docker configuration:

   * `Dockerfile`
   * `docker-compose.yml`
3. Define project structure following `reglas_programacion_django.md`:

   * Snake_case → files, variables, functions
   * PascalCase → classes
   * Header comments (author, date, description)

---

## Phase 2: Core Models

Create models in separate files (`snake_case.py`):

### Models

* **Factura (Invoice)**

  * numero_factura
  * monto
  * fecha
  * cliente_nit
  * archivo (PDF/imagen)
  * ocr_data

* **CertificadoBancario (BankCertificate)**

  * numero_referencia
  * monto
  * fecha
  * cliente_nit
  * archivo

* **DetallePago (PaymentDetail)**

  * factura (FK)
  * certificado (FK)
  * estado_match
  * diferencias
  * resumen

* **Cliente (Client)**

  * nit
  * nombre
  * contacto

* **Usuario (User)**

  * Extiende Django auth
  * rol (contador/admin)

✔ Cada modelo incluye:

* `__str__()`
* Relaciones con `ForeignKey`

---

## Phase 3: OCR Service (Advanced Feature #1)

Archivo: `services/ocr_service.py`

Funciones:

* Usar **PyMuPDF (fitz)** para PDFs
* Usar **Tesseract + Pillow** para imágenes
* Extraer:

  * Número de factura
  * Monto
  * Fecha
  * NIT

✔ Output: diccionario estructurado

---

## Phase 4: Smart Matching Service (Advanced Feature #2)

Archivo: `services/comparador_pagos.py`

Funciones:

* `comparar_pagos(factura_data, certificado_data)`
* `generar_resumen_pagos()`

Validaciones:

* Diferencias de monto
* Fechas inconsistentes
* NIT faltante

---

## Phase 5: Views & Templates

###  User Views (read-only)

* `consulta_facturas()` → listar/buscar
* `consulta_pagos()` → estado de pagos
* `dashboard()` → métricas

###  Admin Views (CRUD)

* `admin_facturas()`
* `admin_certificados()`
* `admin_usuarios()`

✔ Reglas:

* Usar `base.html`
* Lógica compleja en **services**, no en views

---

## Phase 6: Dashboard (Advanced Feature #3)

Métricas:

* Total de facturas procesadas
* Tasa de match exitoso
* Validaciones pendientes
* Tiempo ahorrado
* Inconsistencias recientes

---

## Phase 7: Export Reports (Advanced Feature #4)

Archivo: `services/export_service.py`

Funciones:

* `exportar_pdf(resumen_pago)`
* `exportar_excel(datos)`

---

## Phase 8: Authentication & URLs

* Sistema de autenticación de Django
* `@login_required` en admin
* Separación de rutas:

  * `/usuario/`
  * `/admin/`
* `urls.py` con rutas descriptivas

---

## Phase 9: Mock Data & Testing

* `datos_ficticios.py` → generar datos
* Exportar a: `sql/datos_ficticios.sql`

✔ Testing:

* OCR
* Matching
* Dashboard
* Exportaciones

---

#  Critical Files

| File                           | Purpose                       |
| ------------------------------ | ----------------------------- |
| models/factura.py              | Invoice model with OCR fields |
| models/certificado_bancario.py | Bank certificate model        |
| models/detalle_pago.py         | Payment matching results      |
| services/ocr_service.py        | OCR extraction                |
| services/comparador_pagos.py   | Matching logic                |
| services/export_service.py     | Reports generation            |
| views/usuario_views.py         | User views                    |
| views/admin_views.py           | Admin views                   |
| templates/base.html            | Base template                 |
| urls.py                        | Routes                        |
| Dockerfile                     | Container setup               |
| docker-compose.yml             | Multi-container config        |
| datos_ficticios.py             | Mock data generator           |

---

# Verification Checklist

1. `docker-compose up --build` → app runs
2. Upload invoice → OCR works
3. Upload bank certificate → matching works
4. Dashboard → correct metrics
5. Export → PDF/Excel generated
6. Admin → CRUD works
7. User → read-only views

---

#  Compliance (reglas_programacion_django.md)

* DRY principle
* Snake_case naming
* Models → `django.db.models`
* Views → solo render (lógica en services)
* Separación user/admin
* PostgreSQL con migraciones
* Docker obligatorio
* 4 features avanzadas documentadas

---

Paleta de colores: 
- #000000
- #F57C00 
- #F9A825
- #FDD835
- #FFECB3
- #FFFFFF
