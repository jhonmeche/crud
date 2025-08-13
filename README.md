# Taller Servicio Técnico (FastAPI)

Sistema simple para gestionar clientes, equipos y órdenes de servicio de un taller de computadores e impresoras. Envía automáticamente un mensaje de recepción al WhatsApp del cliente usando WhatsApp Cloud API.

## Requisitos
- Python 3.11+ (con `pip` disponible)
- Variables de entorno de WhatsApp Cloud API (ver `.env.example`)

## Instalación
En algunos entornos no es posible crear `venv`. Si puedes, usa:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Si no, instala paquetes en usuario (puede requerir `--break-system-packages`):

```bash
python3 -m pip install --user fastapi "uvicorn[standard]" sqlmodel jinja2 python-dotenv httpx
```

## Variables de entorno
Crea un archivo `.env` en la raíz del proyecto:

```
WHATSAPP_PHONE_NUMBER_ID=1234567890
WHATSAPP_TOKEN=EAAG....
WHATSAPP_API_BASE=https://graph.facebook.com/v19.0
```

- Asegúrate de usar números de cliente en formato E.164 (por ej. `57XXXXXXXXXX`).
- Para pruebas, WhatsApp Cloud API solo envía a números agregados como "testers" o a usuarios que han iniciado conversación con tu número de negocio.

## Ejecutar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abre `http://localhost:8000/`.

## Flujo
- Crea una nueva orden en `Órdenes > Nueva orden`.
- Al guardar, se crea/actualiza el cliente, se registra el equipo y la orden en estado "recibido".
- Se envía un WhatsApp de confirmación al cliente.
- Desde el detalle de la orden, puedes avanzar estados y opcionalmente notificar por WhatsApp.

## Base de datos
SQLite en `app.db` (se crea automáticamente). Para resetear, borra `app.db` (perderás datos).

## Seguridad
Este demo no implementa autenticación. Para producción agrega auth (por ej. OAuth2/Keycloak) y permisos por rol.

## Ejecutar con Docker

```bash
docker build -t taller .
docker run -p 8000:8000 --env-file .env taller
```

Abre `http://<IP_DEL_SERVIDOR>:8000/` desde los teléfonos en la misma red para que los técnicos puedan actualizar órdenes.
