import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9()\-\s+.]{7,20}$")
TICKET_TYPES = {"VIP", "General", "Student"}
STATUSES = {"Active", "Used", "Cancelled"}
PAYMENT_METHODS = {"Card", "Cash", "Online", "Complimentary"}


def clean(value):
    return (value or "").strip()


def blank_to_none(value):
    cleaned = clean(value)
    return cleaned if cleaned else None


def parse_int(value, field_name):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number.")
    if parsed < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return parsed


def parse_money(value, field_name):
    try:
        parsed = Decimal(value)
    except (TypeError, InvalidOperation):
        raise ValueError(f"{field_name} must be a valid number.")
    if parsed < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return parsed


def parse_datetime_input(value, field_name="Event time"):
    cleaned = clean(value)
    if not cleaned:
        raise ValueError(f"{field_name} is required.")
    try:
        return datetime.strptime(cleaned, "%Y-%m-%dT%H:%M")
    except ValueError as exc:
        raise ValueError(f"{field_name} has to come from the date/time picker.") from exc


def validate_event_form(form):
    event_name = clean(form.get("event_name"))
    event_location = clean(form.get("event_location"))
    if not event_name:
        raise ValueError("Event name is required.")
    if not event_location:
        raise ValueError("Event location is required.")

    return {
        "event_name": event_name,
        "event_location": event_location,
        "event_time": parse_datetime_input(form.get("event_time")),
        "capacity": parse_int(form.get("capacity"), "Capacity"),
        "ticket_price": parse_money(form.get("ticket_price"), "Ticket price"),
    }


def validate_attendee_form(form):
    full_name = clean(form.get("full_name"))
    email = clean(form.get("email")).lower()
    phone = blank_to_none(form.get("phone"))

    if not full_name:
        raise ValueError("Full name is required.")
    if not email:
        raise ValueError("Email is required.")
    if not EMAIL_REGEX.match(email):
        raise ValueError("Email is not in a valid format.")
    if phone and not PHONE_REGEX.match(phone):
        raise ValueError("Phone number is not in a valid format.")

    return {"full_name": full_name, "email": email, "phone": phone}


def validate_ticket_form(form):
    ticket_type = clean(form.get("ticket_type"))
    status = clean(form.get("status"))
    if ticket_type not in TICKET_TYPES:
        raise ValueError("Ticket type is not valid.")
    if status not in STATUSES:
        raise ValueError("Status is not valid.")

    return {
        "event_id": parse_int(form.get("event_id"), "Event"),
        "attendee_id": parse_int(form.get("attendee_id"), "Attendee"),
        "ticket_type": ticket_type,
        "privilege": blank_to_none(form.get("privilege")),
        "origin": blank_to_none(form.get("origin")),
        "status": status,
    }


def validate_purchase_form(form):
    payment_method = clean(form.get("payment_method"))
    if payment_method not in PAYMENT_METHODS:
        raise ValueError("Payment method is not valid.")

    purchase_date_value = clean(form.get("purchase_date"))
    if not purchase_date_value:
        raise ValueError("Purchase date is required.")
    try:
        purchase_date = datetime.strptime(purchase_date_value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Purchase date has to come from the date picker.") from exc

    return {
        "ticket_id": parse_int(form.get("ticket_id"), "Ticket"),
        "purchase_date": purchase_date,
        "payment_method": payment_method,
        "amount_paid": parse_money(form.get("amount_paid"), "Amount paid"),
    }
