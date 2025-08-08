from __future__ import annotations

import os
from typing import Optional

import httpx
from dotenv import load_dotenv


load_dotenv()

WABA_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WABA_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WABA_API_BASE = os.getenv("WHATSAPP_API_BASE", "https://graph.facebook.com/v19.0")


class WhatsAppService:
    def __init__(self, phone_number_id: Optional[str] = None, token: Optional[str] = None) -> None:
        self.phone_number_id = phone_number_id or WABA_PHONE_NUMBER_ID
        self.token = token or WABA_TOKEN

    def is_configured(self) -> bool:
        return bool(self.phone_number_id and self.token)

    async def send_text(self, to_phone_e164: str, body_text: str) -> dict:
        if not self.is_configured():
            return {"ok": False, "error": "WhatsApp no configurado (faltan variables de entorno)"}

        url = f"{WABA_API_BASE}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone_e164,
            "type": "text",
            "text": {"body": body_text},
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                return {"ok": False, "status_code": resp.status_code, "body": resp.text}
            try:
                return {"ok": True, "data": resp.json()}
            except Exception:
                return {"ok": True, "data_raw": resp.text}