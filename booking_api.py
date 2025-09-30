# booking_api.py
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime

app = FastAPI()

class Booking(BaseModel):
    name: str
    phone: str
    email: EmailStr
    slot_iso: str          # e.g. "2025-09-26T10:00:00+10:00"
    mode: str              # "video" | "display-suite"
    notes: str | None = None

@app.post("/book_appointment")
def book(b: Booking):
    dt = datetime.fromisoformat(b.slot_iso)
    booking_id = f"RS-{dt:%Y%m%d-%H%M}"
    msg = f"Booked {dt:%a %d %b %H:%M} AEST"
    return {"ok": True, "booking_id": booking_id, "message": msg}
