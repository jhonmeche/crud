from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import Client, Device, WorkOrder, WorkOrderEvent
from app.services.whatsapp import WhatsAppService


router = APIRouter(prefix="/ordenes", tags=["ordenes"])


templates = Jinja2Templates(directory="app/templates")


@router.get("/nueva", response_class=HTMLResponse)
async def new_order_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("workorder_new.html", {"request": request})


@router.post("/")
async def create_order(
    request: Request,
    name: str = Form(...),
    phone_e164: str = Form(...),
    email: Optional[str] = Form(None),
    document: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    device_type: str = Form(...),
    brand: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    serial: Optional[str] = Form(None),
    accessories: Optional[str] = Form(None),
    physical_condition: Optional[str] = Form(None),
    observations: Optional[str] = Form(None),
    issue_description: str = Form(...),
    password: Optional[str] = Form(None),
    estimate_amount: Optional[float] = Form(None),
    session: Session = Depends(get_session),
):
    existing_client = session.exec(select(Client).where(Client.phone_e164 == phone_e164)).first()
    if existing_client is None:
        client = Client(
            name=name,
            phone_e164=phone_e164,
            email=email,
            document=document,
            address=address,
        )
        session.add(client)
        session.commit()
        session.refresh(client)
    else:
        client = existing_client

    device = Device(
        client_id=client.id,
        device_type=device_type,
        brand=brand,
        model=model,
        serial=serial,
        accessories=accessories,
        physical_condition=physical_condition,
        observations=observations,
    )
    session.add(device)
    session.commit()
    session.refresh(device)

    work_order = WorkOrder(
        device_id=device.id,
        status="recibido",
        issue_description=issue_description,
        password=password,
        estimate_amount=estimate_amount,
    )
    session.add(work_order)
    session.commit()
    session.refresh(work_order)

    event = WorkOrderEvent(work_order_id=work_order.id, status="recibido", notes="Equipo recibido")
    session.add(event)
    session.commit()

    # Enviar WhatsApp de recepción
    wa = WhatsAppService()
    receipt_text = (
        f"Hola {client.name}, hemos recibido tu equipo en el taller.\n"
        f"Orden N° {work_order.id}.\n"
        f"Equipo: {device.device_type} {device.brand or ''} {device.model or ''}\n"
        f"Serie: {device.serial or 'N/D'}\n"
        f"Falla reportada: {work_order.issue_description}.\n\n"
        f"Te informaremos avances por este medio. Gracias."
    )
    try:
        await wa.send_text(client.phone_e164, receipt_text)
    except Exception:
        pass

    return RedirectResponse(url=f"/ordenes/{work_order.id}", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def list_orders(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    orders = session.exec(select(WorkOrder).order_by(WorkOrder.created_at.desc())).all()
    # Pre-cargar info relacionada mínima
    devices = {d.id: d for d in session.exec(select(Device).where(Device.id.in_([o.device_id for o in orders]))).all()} if orders else {}
    clients: dict[int, Client] = {}
    for device in devices.values():
        if device.client_id not in clients:
            cli = session.get(Client, device.client_id)
            if cli:
                clients[device.client_id] = cli
    return templates.TemplateResponse(
        "workorder_list.html",
        {"request": request, "orders": orders, "devices": devices, "clients": clients},
    )


@router.get("/{order_id}", response_class=HTMLResponse)
async def order_detail(order_id: int, request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    device = session.get(Device, order.device_id)
    client = session.get(Client, device.client_id) if device else None
    events = session.exec(
        select(WorkOrderEvent).where(WorkOrderEvent.work_order_id == order_id).order_by(WorkOrderEvent.created_at.desc())
    ).all()
    return templates.TemplateResponse(
        "workorder_detail.html",
        {"request": request, "order": order, "device": device, "client": client, "events": events},
    )


@router.post("/{order_id}/evento")
async def add_event(
    order_id: int,
    status: str = Form(...),
    notes: Optional[str] = Form(None),
    notify: Optional[bool] = Form(False),
    session: Session = Depends(get_session),
):
    order = session.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    event = WorkOrderEvent(work_order_id=order_id, status=status, notes=notes)
    session.add(event)

    order.status = status
    session.add(order)

    session.commit()

    if notify:
        device = session.get(Device, order.device_id)
        client = session.get(Client, device.client_id) if device else None
        if client:
            wa = WhatsAppService()
            text = f"Actualización orden {order.id}: {status}. {notes or ''}".strip()
            try:
                await wa.send_text(client.phone_e164, text)
            except Exception:
                pass

    return RedirectResponse(url=f"/ordenes/{order_id}", status_code=303)