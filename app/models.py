from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Client(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2)
    phone_e164: str = Field(index=True, description="Número en formato E.164, ej: 57XXXXXXXXXX")
    email: Optional[str] = Field(default=None, index=True)
    document: Optional[str] = Field(default=None, index=True, description="Documento/NIT")
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id", index=True)
    device_type: str = Field(index=True, description="computador | impresora | otro")
    brand: Optional[str] = None
    model: Optional[str] = None
    serial: Optional[str] = Field(default=None, index=True)
    accessories: Optional[str] = None
    physical_condition: Optional[str] = None
    observations: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: int = Field(foreign_key="device.id", index=True)
    status: str = Field(default="recibido", index=True)
    issue_description: str
    password: Optional[str] = None
    estimate_amount: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkOrderEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    work_order_id: int = Field(foreign_key="workorder.id", index=True)
    status: str = Field(index=True)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)