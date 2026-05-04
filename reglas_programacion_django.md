# Reglas de Programación del Proyecto Django

## 1. Reglas Generales de Programación {#reglas-generales-de-programación}

- Todo el código debe seguir el principio DRY (Don't Repeat Yourself).

- El código debe ser claro, legible y modular.

- Cada archivo debe incluir en la parte superior un comentario con nombre del autor, fecha y descripción.

- Los nombres de variables, funciones y clases deben estar en inglés.

- Se deben usar nombres descriptivos.

- Todo cambio en el código debe realizarse mediante commit y push al repositorio GitHub.

- El arquitecto puede revertir cambios que no sigan estas reglas.

- Evitar lógica compleja dentro de las vistas.

## 2. Convención para Nombrar Variables, Funciones y Clases {#convención-para-nombrar-variables-funciones-y-clases}

- Las variables deben escribirse en snake_case (minúsculas separadas por guiones bajos).

- Ejemplos de variables correctas: numero_factura, monto_pagado, fecha_pago, lista_facturas.

- No se deben usar abreviaciones innecesarias o nombres poco descriptivos.

- Las funciones también deben escribirse en snake_case.

- Ejemplos de funciones: extraer_datos_factura(), comparar_pagos(), generar_resumen_pagos().

- Las clases deben escribirse en PascalCase.

- Ejemplos de clases: Factura, CertificadoBancario, DetallePago, ComparadorPagos.

- Los archivos deben nombrarse en snake_case.

- Ejemplos: factura_model.py, comparador_pagos.py, ocr_service.py.

- Las constantes deben escribirse en MAYÚSCULAS con guiones bajos.

- Ejemplos: MAX_INTENTOS_LOGIN, RUTA_ARCHIVOS_FACTURAS.

## 3. Reglas para Modelos (Models) {#reglas-para-modelos-models}

- Cada entidad del diagrama de clases debe implementarse como un modelo en Django.

- Todos los modelos deben extender de django.db.models.

- Cada modelo debe incluir atributos definidos y el método \_\_str\_\_().

- Las relaciones deben implementarse con ForeignKey, ManyToManyField o OneToOneField.

- Todo cambio debe generar una migration usando makemigrations y migrate.

- No modificar la base de datos directamente.

## 4. Reglas para Vistas (Views) {#reglas-para-vistas-views}

- Toda funcionalidad visible debe implementarse en una vista Django.

- Toda vista debe estar asociada a una ruta en urls.py.

- Las vistas deben retornar templates HTML.

- La lógica compleja debe implementarse en funciones auxiliares o servicios.

- Las vistas deben validar los datos recibidos.

## 5. Reglas para Templates {#reglas-para-templates}

- Todos los templates deben ser archivos HTML.

- Todos los templates deben extender de base.html.

- Los templates deben ubicarse en la carpeta templates/.

- No colocar lógica compleja dentro del HTML.

## 6. Reglas para URLs {#reglas-para-urls}

- Toda ruta debe estar asociada a una vista.

- Las rutas se definen en urls.py.

- Las rutas deben usar nombres claros y descriptivos.

- Las rutas del usuario final deben ser diferentes a las del administrador.

## 7. Reglas para la Base de Datos {#reglas-para-la-base-de-datos}

- La base de datos utilizada será PostgreSQL.

- Todas las modificaciones deben realizarse mediante migrations de Django.

- Se deben crear datos ficticios para pruebas.

- Cuando haya suficientes datos, se debe exportar el SQL y subirlo al repositorio.

## 8. Reglas para Autenticación {#reglas-para-autenticación}

- El sistema debe utilizar el sistema de autenticación de Django.

- Las vistas del administrador deben requerir login.

- Los usuarios deben autenticarse antes de acceder a funcionalidades.

## 9. Separación de Secciones {#separación-de-secciones}

- Debe existir una sección para usuario final y otra para administrador.

- El usuario final solo puede consultar información.

- El administrador puede crear, editar y eliminar registros.

- Las vistas del administrador no deben compartirse con las del usuario final.

## 10. Reglas para Docker {#reglas-para-docker}

- El proyecto debe ejecutarse usando Docker.

- El proyecto debe incluir Dockerfile y docker-compose.yml.

- Todos los integrantes deben probar el sistema con Docker antes de hacer push.

## 11. Reglas para el Repositorio GitHub {#reglas-para-el-repositorio-github}

- Realizar commits frecuentes.

- Cada commit debe tener un mensaje claro y descriptivo.

- No subir archivos innecesarios.

- El repositorio debe incluir README.md, código fuente, SQL ficticio y documentación.

## 12. Funcionalidades Interesantes {#funcionalidades-interesantes}

- El sistema debe incluir al menos 4 funcionalidades avanzadas.

- Cada funcionalidad debe documentarse en el Wiki indicando archivo y línea de implementación.

## 13. Documentación {#documentación}

- El repositorio debe contener README.md con instrucciones de ejecución.

- El proyecto debe incluir documentación en el Wiki.

- Se deben incluir guía de estilo y reglas de programación.
