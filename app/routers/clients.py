from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import Client


router = APIRouter(prefix="/clientes", tags=["clientes"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def list_clients(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    clients = session.exec(select(Client).order_by(Client.created_at.desc())).all()
    return templates.TemplateResponse("clients_list.html", {"request": request, "clients": clients})