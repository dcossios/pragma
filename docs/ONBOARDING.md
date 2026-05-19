# Onboarding para desarrolladores — Pragma

Guía para incorporarte al proyecto: levantar el entorno, entender los flujos principales y saber dónde modificar el código.

Para detalles técnicos profundos (modelo de datos, matching, OCR, despliegue), consulta [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Qué es Pragma

Pragma es una aplicación Django que ayuda a firmas contables a **verificar pagos más rápido**: lee facturas con OCR, permite revisar los datos extraídos, las compara con certificados bancarios y muestra el estado del matching en un dashboard con exportes PDF y Excel.

Está orientada a un entorno controlado (firma pequeña, ~6 personas) con localización para Guatemala.

---

## Prerrequisitos

| Herramienta | Versión | Obligatorio |
|-------------|---------|-------------|
| Python | 3.11+ | Sí |
| pip | Reciente | Sí |
| Docker + Docker Compose | Cualquier versión estable | Solo si usas el stack containerizado |
| Tesseract OCR | Sistema | Solo ejecución **local sin Docker** |
| PostgreSQL | 15+ | Solo si corres sin Docker y sin SQLite |

---

## Primer día — checklist

- [ ] Clonar el repositorio
- [ ] Elegir modo de ejecución (Docker, SQLite local o PostgreSQL local)
- [ ] Instalar dependencias y aplicar migraciones
- [ ] Crear un superusuario Django
- [ ] (Opcional) Cargar datos ficticios
- [ ] Abrir la app en el navegador y recorrer los flujos
- [ ] Ejecutar la suite de pruebas
- [ ] Leer [ARCHITECTURE.md](ARCHITECTURE.md) y [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Tres formas de ejecutar el proyecto

Los pasos detallados de instalación están en el [README.md](../README.md). Resumen con **puertos correctos**:

| Modo | URL de la app | Base de datos | Puerto DB (host) |
|------|---------------|---------------|------------------|
| **Docker** | `http://localhost:8001` | PostgreSQL en contenedor | `localhost:5433` |
| **SQLite local** | `http://127.0.0.1:8000` | `db.sqlite3` en la raíz | — |
| **PostgreSQL local** | `http://127.0.0.1:8000` | Tu instancia Postgres | Según tu config |

> Con Docker, el puerto **8001** en el host mapea al 8000 del contenedor (`docker-compose.yml`). Sin Docker, `runserver` escucha en **8000** por defecto.

### Opción A — Docker (recomendado para entorno homogéneo)

```bash
cp .env.example .env
# Completar SECRET_KEY, POSTGRES_* y USE_SQLITE=False en .env
docker-compose up --build
```

Abrir: `http://localhost:8001`

### Opción B — SQLite local (más rápido para desarrollo)

```bash
python3 -m pip install -r requirements.txt
USE_SQLITE=True python3 manage.py migrate
USE_SQLITE=True python3 manage.py runserver
```

Abrir: `http://127.0.0.1:8000`

### Opción C — PostgreSQL local (sin Docker)

Configura las variables `POSTGRES_*` y `DB_HOST=localhost`, luego:

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

---

## Variables de entorno

Plantilla: `.env.example`. En Docker, Compose carga `.env` automáticamente.

| Variable | Descripción | Valor típico (dev) |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta Django | Cadena aleatoria larga |
| `DEBUG` | Modo depuración | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |
| `USE_SQLITE` | Usar SQLite en lugar de Postgres | `True` (local rápido) / `False` (Docker) |
| `POSTGRES_DB` | Nombre de la base | `pragma_db` |
| `POSTGRES_USER` | Usuario Postgres | `pragma_user` |
| `POSTGRES_PASSWORD` | Contraseña Postgres | `pragma_password` |
| `DB_HOST` | Host de la base | `db` (Docker) / `localhost` (local) |
| `DB_PORT` | Puerto Postgres | `5432` |
| `TESSDATA_PREFIX` | Ruta datos Tesseract | Solo si Tesseract no encuentra idiomas |

Configuración en código: `pragma/settings.py`.

---

## Usuarios y roles

### Modelo de usuarios

Pragma usa dos capas:

1. **`User`** (Django auth) — credenciales de login.
2. **`Usuario`** (perfil) — rol del negocio, vinculado con `OneToOneField` y `related_name="perfil"`.

### Roles disponibles

| Rol | Código | Qué puede hacer |
|-----|--------|-----------------|
| Contador | `contador` | `/usuario/*`: dashboard, facturas, pagos, exportes |
| Administrador | `admin` | Todo lo anterior + `/admin-panel/*`: CRUD facturas, certificados, usuarios |
| Superusuario | — | Acceso total, incluido `/admin/` y bypass del gate de admin-panel |

### Crear el primer superusuario

```bash
USE_SQLITE=True python3 manage.py createsuperuser
```

El superusuario puede entrar a `/admin/` y al `/admin-panel/` sin perfil `Usuario`, pero para probar flujos de contador conviene crear un usuario con perfil.

### Crear un contador o admin desde la UI

1. Iniciar sesión como admin en `/admin-panel/usuarios/`.
2. Completar el formulario de creación (username, contraseña, rol).

También puedes crear usuarios desde `/admin/` (Django admin) y asociar el perfil `Usuario` manualmente.

---

## Tour funcional

### Flujo del contador (`/usuario/`)

1. **Login** — `/usuario/login/`
2. **Dashboard** — `/usuario/dashboard/`  
   Métricas: facturas procesadas, matches, validaciones pendientes, tiempo ahorrado estimado.
3. **Cargar factura** — `/usuario/facturas/cargar/`  
   Subir PDF o imagen → OCR automático.
4. **Revisar factura** — `/usuario/facturas/revisar/`  
   Corregir número, NIT, monto y fecha antes de guardar.
5. **Consultar facturas** — `/usuario/facturas/?q=`  
   Búsqueda por texto.
6. **Consultar pagos** — `/usuario/pagos/?estado=match|partial|no_match`  
   Ver resultados del matching.
7. **Exportar** — PDF por pago individual o Excel de todos los pagos filtrados.

### Flujo del administrador (`/admin-panel/`)

1. **Facturas** — listado, carga con OCR, edición y eliminación.
2. **Certificados bancarios** — captura manual (sin OCR); al guardar se busca factura candidata y se crea `DetallePago` si aplica.
3. **Usuarios** — alta, edición de rol y eliminación.

### Django admin nativo (`/admin/`)

CRUD directo sobre todos los modelos. Útil para depuración; la operación diaria de negocio usa `/usuario/` y `/admin-panel/`.

---

## Datos de prueba

### Comando de management

```bash
USE_SQLITE=True python3 manage.py cargar_datos_ficticios --clientes 5 --facturas-por-cliente 3
```

### Script auxiliar

```bash
USE_SQLITE=True python3 datos_ficticios.py 5 3
```

### SQL de ejemplo

Archivo: `sql/datos_ficticios.sql` — inserts de referencia para cargar manualmente en Postgres.

---

## Comandos útiles

```bash
# Migraciones
USE_SQLITE=True python3 manage.py migrate

# Servidor de desarrollo
USE_SQLITE=True python3 manage.py runserver

# Shell interactivo
USE_SQLITE=True python3 manage.py shell

# Pruebas
USE_SQLITE=True python3 manage.py test -v 2

# Recolectar estáticos (si cambias assets)
USE_SQLITE=True python3 manage.py collectstatic

# Crear migraciones tras cambiar modelos
USE_SQLITE=True python3 manage.py makemigrations core
```

---

## Convenciones del equipo

Resumen; el detalle está en los documentos enlazados.

| Elemento | Convención |
|----------|------------|
| Variables y funciones | `snake_case` |
| Clases | `PascalCase` |
| Constantes | `UPPER_CASE` |
| Archivos Python | `snake_case.py` |
| Commits | [Conventional Commits](../CONTRIBUTING.md) (`feat:`, `fix:`, `docs:`, etc.) |
| Ramas | `tipo/descripcion-corta` (ej. `feat/ocr-mejoras`) |

Documentos de referencia:

- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR checklist y commits
- [reglas_programacion_django.md](../reglas_programacion_django.md) — reglas Django del proyecto (DRY, capas, templates)

---

## Dónde tocar el código

Guía rápida según el cambio que quieras hacer:

| Si quieres cambiar… | Edita… |
|---------------------|--------|
| Reglas de matching (score, umbrales) | `pragma/core/services/comparador_pagos.py` |
| Extracción OCR o patrones regex | `pragma/core/services/ocr_service.py` |
| Pipeline guardar factura / certificado | `pragma/core/services/factura_service.py` |
| Métricas del dashboard | `pragma/core/services/dashboard_service.py` |
| Exportes PDF/Excel | `pragma/core/services/export_service.py` |
| Pantallas del contador | `pragma/core/views/usuario_views.py` + `templates/usuario/` |
| Panel admin personalizado | `pragma/core/views/admin_views.py` + `templates/admin_panel/` |
| Validación de formularios / uploads | `pragma/core/forms.py` |
| Modelos o relaciones | `pragma/core/models/` + nueva migración |
| Permisos admin-panel | `pragma/core/permissions.py` |
| Rutas URL | `pragma/core/urls_usuario.py`, `urls_admin.py`, `pragma/urls.py` |
| Config global (DB, locale, media) | `pragma/settings.py` |
| Estilos y layout base | `templates/base.html`, `static_src/` |

Mantén la lógica de negocio en **services**, no en views.

---

## Ejecutar pruebas

```bash
USE_SQLITE=True python3 manage.py test -v 2
```

Antes de abrir un PR, verifica que las pruebas pasen y que tu código sigue las convenciones de [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Troubleshooting

### `TesseractNotFoundError` o OCR falla en local

Instala Tesseract en el sistema:

- **macOS:** `brew install tesseract tesseract-lang`
- **Ubuntu/Debian:** `sudo apt install tesseract-ocr tesseract-ocr-spa`

Con Docker, Tesseract ya está en la imagen.

### Puerto 8001 u 8000 en uso

- Docker: cambia el mapeo en `docker-compose.yml` (`"8002:8000"`).
- Local: `python3 manage.py runserver 8002`

### No puedo acceder a `/admin-panel/` (403)

Tu usuario necesita `perfil.rol == "admin"` o ser superusuario. Un contador solo tiene acceso a `/usuario/`.

### La app en Docker no responde en `localhost:8000`

Con Docker debes usar **`http://localhost:8001`**, no 8000.

### Variables de entorno no se aplican en local

`python-dotenv` no se carga automáticamente. Exporta variables en la shell:

```bash
export USE_SQLITE=True
export DEBUG=True
```

O usa Docker Compose con archivo `.env`.

### Enlace al admin-panel no aparece en la navbar

Conocido: `templates/base.html` referencia `user.usuario.rol` pero el perfil se accede como `user.perfil`. Ver [ARCHITECTURE.md](ARCHITECTURE.md#limitaciones-y-deuda-técnica-conocida).

### Base de datos vacía tras `docker-compose down -v`

El flag `-v` elimina volúmenes de Postgres. Vuelve a ejecutar `migrate` y `createsuperuser`.

---

## Próximos pasos

1. Leer [ARCHITECTURE.md](ARCHITECTURE.md) para entender flujos OCR y matching.
2. Revisar [PLAN.md](../PLAN.md) para ver fases pendientes del producto.
3. Elegir una tarea pequeña y abrir una rama siguiendo [CONTRIBUTING.md](../CONTRIBUTING.md).
4. Antes del PR: pruebas verdes + checklist de nombres y commits.

---

## Documentación relacionada

- [README.md](../README.md) — referencia rápida de instalación
- [ARCHITECTURE.md](ARCHITECTURE.md) — arquitectura técnica
- [PLAN.md](../PLAN.md) — roadmap del producto
- [CONTRIBUTING.md](../CONTRIBUTING.md) — cómo contribuir
