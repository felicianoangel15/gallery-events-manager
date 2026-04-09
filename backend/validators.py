import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9()\-\s+.]{7,20}$")
TICKET_TYPES = {"VIP", "General", "Student"}
STATUSES = {"Active", "Used", "Cancelled"}
PAYMENT_METHODS = {"Card", "Cash", "Online", "Complimentary"}


def clean_text(value):
    return (value or "").strip()


def optional_text(value):
    cleaned = clean_text(value)
    return cleaned if cleaned else None


def parse_non_negative_int(value, field_name):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.")
    if parsed < 0:
        raise ValueError(f"{field_name} must be 0 or greater.")
    return parsed


def parse_non_negative_decimal(value, field_name):
    try:
        parsed = Decimal(value)
    except (TypeError, InvalidOperation):
        raise ValueError(f"{field_name} must be a valid number.")
    if parsed < 0:
        raise ValueError(f"{field_name} must be 0 or greater.")
    return parsed


def parse_datetime_local(value, field_name="Event time"):
    cleaned = clean_text(value)
    if not cleaned:
        raise ValueError(f"{field_name} is required.")
    try:
        return datetime.strptime(cleaned, "%Y-%m-%dT%H:%M")
    except ValueError as exc:
        raise ValueError(f"{field_name} must use the date/time picker.") from exc


def validate_event_form(form):
    event_name = clean_text(form.get("event_name"))
    event_location = clean_text(form.get("event_location"))
    if not event_name:
        raise ValueError("Event name is required.")
    if not event_location:
        raise ValueError("Event location is required.")

    return {
        "event_name": event_name,
        "event_location": event_location,
        "event_time": parse_datetime_local(form.get("event_time")),
        "capacity": parse_non_negative_int(form.get("capacity"), "Capacity"),
        "ticket_price": parse_non_negative_decimal(form.get("ticket_price"), "Ticket price"),
    }


def validate_attendee_form(form):
    full_name = clean_text(form.get("full_name"))
    email = clean_text(form.get("email")).lower()
    phone = optional_text(form.get("phone"))

    if not full_name:
        raise ValueError("Full name is required.")
    if not email:
        raise ValueError("Email is required.")
    if not EMAIL_REGEX.match(email):
        raise ValueError("Email format is invalid.")
    if phone and not PHONE_REGEX.match(phone):
        raise ValueError("Phone format is invalid.")

    return {"full_name": full_name, "email": email, "phone": phone}


def validate_ticket_form(form):
    ticket_type = clean_text(form.get("ticket_type"))
    status = clean_text(form.get("status"))
    if ticket_type not in TICKET_TYPES:
        raise ValueError("Ticket type is invalid.")
    if status not in STATUSES:
        raise ValueError("Status is invalid.")

    return {
        "event_id": parse_non_negative_int(form.get("event_id"), "Event"),
        "attendee_id": parse_non_negative_int(form.get("attendee_id"), "Attendee"),
        "ticket_type": ticket_type,
        "privilege": optional_text(form.get("privilege")),
        "origin": optional_text(form.get("origin")),
        "status": status,
    }


def validate_purchase_form(form):
    payment_method = clean_text(form.get("payment_method"))
    if payment_method not in PAYMENT_METHODS:
        raise ValueError("Payment method is invalid.")

    purchase_date_value = clean_text(form.get("purchase_date"))
    if not purchase_date_value:
        raise ValueError("Purchase date is required.")
    try:
        purchase_date = datetime.strptime(purchase_date_value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Purchase date must use the date picker.") from exc

    return {
        "ticket_id": parse_non_negative_int(form.get("ticket_id"), "Ticket"),
        "purchase_date": purchase_date,
        "payment_method": payment_method,
        "amount_paid": parse_non_negative_decimal(form.get("amount_paid"), "Amount paid"),
    }
