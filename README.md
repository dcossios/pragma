# Pragma - Django OCR Invoice Processing System

Aplicación Django para automatizar lectura OCR de facturas, compararlas contra certificados bancarios y exponer métricas/exportes para firmas contables.

## Requisitos

- Python 3.11+
- pip
- Docker + Docker Compose (opcional, recomendado para entorno homogéneo)
- Tesseract OCR (solo para ejecución local sin Docker)

## Variables de entorno clave

- `USE_SQLITE=True|False`  
  Usa SQLite cuando está en `True`. Si está en `False`, usa PostgreSQL.
- `DEBUG=True|False`
- `SECRET_KEY=...`
- `ALLOWED_HOSTS=localhost,127.0.0.1`
- `POSTGRES_DB=pragma_db`
- `POSTGRES_USER=pragma_user`
- `POSTGRES_PASSWORD=pragma_password`
- `DB_HOST=db` (o `localhost` en local)
- `DB_PORT=5432`

## Ejecución con Docker (PostgreSQL)

1) Construir y levantar servicios:

```bash
docker-compose up --build
```

2) Abrir aplicación:

- App: `http://localhost:8001`
- Base de datos PostgreSQL expuesta en host: `localhost:5433`

3) Detener servicios:

```bash
docker-compose down
```

Para eliminar también volúmenes de datos:

```bash
docker-compose down -v
```

## Ejecución local rápida (SQLite)

1) Instalar dependencias:

```bash
python3 -m pip install -r requirements.txt
```

2) Migrar base de datos:

```bash
USE_SQLITE=True python3 manage.py migrate
```

3) Iniciar servidor:

```bash
USE_SQLITE=True python3 manage.py runserver
```

4) Abrir aplicación:

- App: `http://127.0.0.1:8000`

## Ejecución local con PostgreSQL (sin Docker)

Configura variables de entorno con tu instancia PostgreSQL y ejecuta:

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

## Cargar datos ficticios

Comando de management:

```bash
USE_SQLITE=True python3 manage.py cargar_datos_ficticios --clientes 5 --facturas-por-cliente 3
```

Script auxiliar:

```bash
USE_SQLITE=True python3 datos_ficticios.py 5 3
```

## Pruebas

```bash
USE_SQLITE=True python3 manage.py test -v 2
```

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md) — stack, modelo de dominio, flujos OCR/matching, despliegue
- [Onboarding para desarrolladores](docs/ONBOARDING.md) — primer día, roles, tour funcional, troubleshooting

## Secciones de la aplicación

- Usuario final: `/usuario/`
- Admin personalizado (CRUD): `/admin-panel/`
- Django admin nativo: `/admin/`

## Funcionalidades avanzadas implementadas

- OCR de facturas: `pragma/core/services/ocr_service.py`
- Matching inteligente de pagos: `pragma/core/services/comparador_pagos.py`
- Dashboard de métricas: `pragma/core/services/dashboard_service.py` + `templates/usuario/dashboard.html`
- Exportes PDF/Excel: `pragma/core/services/export_service.py`

## SQL de ejemplo

- Archivo: `sql/datos_ficticios.sql`

## Convenciones de nombres (resumen)

- Variables y funciones: `snake_case`
- Clases: `PascalCase`
- Constantes: `UPPER_CASE`
- Archivos Python: `snake_case.py`

Consulta el detalle completo en `reglas_programacion_django.md` y `CONTRIBUTING.md`.
