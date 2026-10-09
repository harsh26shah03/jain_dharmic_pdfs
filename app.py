"""
Stage 1: the simplest WhatsApp bot - replies "hi" to every message.
Run:  uvicorn app:app --host 0.0.0.0 --port 8000
"""
import logging
import os

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

load_dotenv()
log = logging.getLogger("hibot")

WA_TOKEN = os.environ["WHATSAPP_TOKEN"]
PHONE_ID = os.environ["PHONE_NUMBER_ID"]
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]

app = FastAPI()


async def send_text(to: str, body: str):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {WA_TOKEN}"},
            json={"messaging_product": "whatsapp", "to": to,
                  "type": "text", "text": {"body": body}})
    if r.is_error:
        log.error("WhatsApp error %s %s", r.status_code, r.text)


async def process(data: dict):
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            # delivery/read receipts arrive here too, but have no "messages" key
            for msg in change.get("value", {}).get("messages", []) or []:
                await send_text(msg["from"], "hi")


@app.get("/webhook", response_class=PlainTextResponse)
async def verify(mode: str | None = Query(None, alias="hub.mode"),
                 token: str | None = Query(None, alias="hub.verify_token"),
                 challenge: str = Query("", alias="hub.challenge")):
    """Meta calls this once when you save the webhook URL."""
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    raise HTTPException(403)


@app.post("/webhook")
async def receive(request: Request, background: BackgroundTasks):
    try:
        data = await request.json()
    except ValueError:
        data = {}
    background.add_task(process, data)
    return {"status": "ok"}