from datetime import datetime

import psycopg2
from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import execute_commit, fetch_all, fetch_one
from validators import (
    PAYMENT_METHODS,
    STATUSES,
    TICKET_TYPES,
    validate_attendee_form,
    validate_event_form,
    validate_purchase_form,
    validate_ticket_form,
)


main_bp = Blueprint("main", __name__)


def format_datetime_input(value):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime("%Y-%m-%dT%H:%M")


def get_dashboard_data():
    metrics = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM events) AS event_count,
            (SELECT COUNT(*) FROM attendees) AS attendee_count,
            (SELECT COUNT(*) FROM tickets) AS ticket_count,
            (SELECT COALESCE(SUM(amount_paid), 0) FROM purchases) AS total_revenue
        """
    )

    upcoming_events = fetch_all(
        """
        SELECT event_id, event_name, event_location, event_time, capacity, ticket_price
        FROM events
        WHERE event_time >= CURRENT_TIMESTAMP
        ORDER BY event_time ASC
        LIMIT 5
        """
    )

    recent_purchases = fetch_all(
        """
        SELECT
            p.purchase_id,
            p.purchase_date,
            p.amount_paid,
            e.event_name,
            a.full_name
        FROM purchases p
        JOIN tickets t ON p.ticket_id = t.ticket_id
        JOIN events e ON t.event_id = e.event_id
        JOIN attendees a ON t.attendee_id = a.attendee_id
        ORDER BY p.purchase_date DESC, p.purchase_id DESC
        LIMIT 5
        """
    )

    return metrics, upcoming_events, recent_purchases


def get_event_choices():
    return fetch_all(
        """
        SELECT event_id, event_name, event_time
        FROM events
        ORDER BY event_time ASC, event_name ASC
        """
    )


def get_attendee_choices():
    return fetch_all(
        """
        SELECT attendee_id, full_name, email
        FROM attendees
        ORDER BY full_name ASC
        """
    )


def get_ticket_choices():
    return fetch_all(
        """
        SELECT
            t.ticket_id,
            e.event_name,
            a.full_name,
            t.status
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        JOIN attendees a ON t.attendee_id = a.attendee_id
        LEFT JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE p.purchase_id IS NULL
        ORDER BY t.ticket_id ASC
        """
    )


@main_bp.route("/")
def dashboard():
    metrics, upcoming_events, recent_purchases = get_dashboard_data()
    return render_template(
        "dashboard.html",
        metrics=metrics,
        upcoming_events=upcoming_events,
        recent_purchases=recent_purchases,
    )


@main_bp.route("/events")
def events():
    events_list = fetch_all(
        """
        SELECT event_id, event_name, event_location, event_time, capacity, ticket_price
        FROM events
        ORDER BY event_time ASC, event_name ASC
        """
    )
    return render_template("events.html", events=events_list, form_data={})


@main_bp.route("/events/add", methods=["POST"])
def add_event():
    try:
        data = validate_event_form(request.form)
        execute_commit(
            """
            INSERT INTO events (event_name, event_location, event_time, capacity, ticket_price)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                data["event_name"],
                data["event_location"],
                data["event_time"],
                data["capacity"],
                data["ticket_price"],
            ),
        )
        flash("Event added.", "success")
        return redirect(url_for("main.events"))
    except ValueError as exc:
        flash(str(exc), "error")
    except psycopg2.Error as exc:
        flash(f"Database error: {exc.pgerror or str(exc)}", "error")

    events_list = fetch_all(
        """
        SELECT event_id, event_name, event_location, event_time, capacity, ticket_price
        FROM events
        ORDER BY event_time ASC, event_name ASC
        """
    )
    return render_template("events.html", events=events_list, form_data=request.form), 400


@main_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id):
    event = fetch_one(
        """
        SELECT event_id, event_name, event_location, event_time, capacity, ticket_price
        FROM events
        WHERE event_id = %s
        """,
        (event_id,),
    )
    if not event:
        flash("Event not found.", "error")
        return redirect(url_for("main.events"))

    if request.method == "POST":
        try:
            data = validate_event_form(request.form)
            execute_commit(
                """
                UPDATE events
                SET event_name = %s,
                    event_location = %s,
                    event_time = %s,
                    capacity = %s,
                    ticket_price = %s
                WHERE event_id = %s
                """,
                (
                    data["event_name"],
                    data["event_location"],
                    data["event_time"],
                    data["capacity"],
                    data["ticket_price"],
                    event_id,
                ),
            )
            flash("Event updated.", "success")
            return redirect(url_for("main.events"))
        except ValueError as exc:
            flash(str(exc), "error")
        except psycopg2.Error as exc:
            flash(f"Database error: {exc.pgerror or str(exc)}", "error")
            event.update(request.form)

    event["event_time_form"] = format_datetime_input(event["event_time"])
    return render_template("event_form.html", event=event)


@main_bp.route("/events/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id):
    try:
        execute_commit("DELETE FROM events WHERE event_id = %s", (event_id,))
        flash("Event deleted.", "success")
    except psycopg2.Error:
        flash("Can't delete that event while related records still exist.", "error")
    return redirect(url_for("main.events"))


@main_bp.route("/attendees")
def attendees():
    attendee_list = fetch_all(
        """
        SELECT attendee_id, full_name, email, phone
        FROM attendees
        ORDER BY full_name ASC, attendee_id ASC
        """
    )
    return render_template("attendees.html", attendees=attendee_list, form_data={})


@main_bp.route("/attendees/add", methods=["POST"])
def add_attendee():
    try:
        data = validate_attendee_form(request.form)
        execute_commit(
            """
            INSERT INTO attendees (full_name, email, phone)
            VALUES (%s, %s, %s)
            """,
            (data["full_name"], data["email"], data["phone"]),
        )
        flash("Attendee added.", "success")
        return redirect(url_for("main.attendees"))
    except ValueError as exc:
        flash(str(exc), "error")
    except psycopg2.Error as exc:
        if exc.pgcode == "23505":
            flash("That email already exists.", "error")
        else:
            flash(f"Database error: {exc.pgerror or str(exc)}", "error")

    attendee_list = fetch_all(
        """
        SELECT attendee_id, full_name, email, phone
        FROM attendees
        ORDER BY full_name ASC, attendee_id ASC
        """
    )
    return render_template("attendees.html", attendees=attendee_list, form_data=request.form), 400


@main_bp.route("/tickets")
def tickets():
    ticket_list = fetch_all(
        """
        SELECT
            t.ticket_id,
            e.event_name,
            a.full_name,
            t.ticket_type,
            t.privilege,
            t.origin,
            t.status
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        JOIN attendees a ON t.attendee_id = a.attendee_id
        ORDER BY t.ticket_id ASC
        """
    )
    return render_template(
        "tickets.html",
        tickets=ticket_list,
        events=get_event_choices(),
        attendees=get_attendee_choices(),
        form_data={},
        ticket_types=sorted(TICKET_TYPES),
        statuses=sorted(STATUSES),
    )


@main_bp.route("/tickets/add", methods=["POST"])
def add_ticket():
    try:
        data = validate_ticket_form(request.form)
        execute_commit(
            """
            INSERT INTO tickets (
                event_id,
                attendee_id,
                ticket_type,
                privilege,
                origin,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                data["event_id"],
                data["attendee_id"],
                data["ticket_type"],
                data["privilege"],
                data["origin"],
                data["status"],
            ),
        )
        flash("Ticket added.", "success")
        return redirect(url_for("main.tickets"))
    except ValueError as exc:
        flash(str(exc), "error")
    except psycopg2.Error as exc:
        flash(f"Database error: {exc.pgerror or str(exc)}", "error")

    ticket_list = fetch_all(
        """
        SELECT
            t.ticket_id,
            e.event_name,
            a.full_name,
            t.ticket_type,
            t.privilege,
            t.origin,
            t.status
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        JOIN attendees a ON t.attendee_id = a.attendee_id
        ORDER BY t.ticket_id ASC
        """
    )
    return render_template(
        "tickets.html",
        tickets=ticket_list,
        events=get_event_choices(),
        attendees=get_attendee_choices(),
        form_data=request.form,
        ticket_types=sorted(TICKET_TYPES),
        statuses=sorted(STATUSES),
    ), 400


@main_bp.route("/purchases")
def purchases():
    purchase_list = fetch_all(
        """
        SELECT
            p.purchase_id,
            p.purchase_date,
            p.payment_method,
            p.amount_paid,
            t.ticket_id,
            e.event_name,
            a.full_name
        FROM purchases p
        JOIN tickets t ON p.ticket_id = t.ticket_id
        JOIN events e ON t.event_id = e.event_id
        JOIN attendees a ON t.attendee_id = a.attendee_id
        ORDER BY p.purchase_date DESC, p.purchase_id DESC
        """
    )
    return render_template(
        "purchases.html",
        purchases=purchase_list,
        tickets=get_ticket_choices(),
        payment_methods=sorted(PAYMENT_METHODS),
        form_data={},
    )


@main_bp.route("/purchases/add", methods=["POST"])
def add_purchase():
    try:
        data = validate_purchase_form(request.form)
        execute_commit(
            """
            INSERT INTO purchases (ticket_id, purchase_date, payment_method, amount_paid)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["ticket_id"],
                data["purchase_date"],
                data["payment_method"],
                data["amount_paid"],
            ),
        )
        flash("Purchase added.", "success")
        return redirect(url_for("main.purchases"))
    except ValueError as exc:
        flash(str(exc), "error")
    except psycopg2.Error as exc:
        if exc.pgcode == "23505":
            flash("A purchase already exists for that ticket.", "error")
        else:
            flash(f"Database error: {exc.pgerror or str(exc)}", "error")

    purchase_list = fetch_all(
        """
        SELECT
            p.purchase_id,
            p.purchase_date,
            p.payment_method,
            p.amount_paid,
            t.ticket_id,
            e.event_name,
            a.full_name
        FROM purchases p
        JOIN tickets t ON p.ticket_id = t.ticket_id
        JOIN events e ON t.event_id = e.event_id
        JOIN attendees a ON t.attendee_id = a.attendee_id
        ORDER BY p.purchase_date DESC, p.purchase_id DESC
        """
    )
    return render_template(
        "purchases.html",
        purchases=purchase_list,
        tickets=get_ticket_choices(),
        payment_methods=sorted(PAYMENT_METHODS),
        form_data=request.form,
    ), 400


@main_bp.route("/reports")
def reports():
    report_data = {
        "upcoming_events": fetch_all(
            """
            SELECT event_id, event_name, event_location, event_time
            FROM events
            WHERE event_time >= CURRENT_TIMESTAMP
            ORDER BY event_time ASC
            """
        ),
        "ticket_counts": fetch_all(
            """
            SELECT
                e.event_name,
                COUNT(t.ticket_id) AS total_tickets
            FROM events e
            LEFT JOIN tickets t ON e.event_id = t.event_id
            GROUP BY e.event_id, e.event_name
            ORDER BY total_tickets DESC, e.event_name ASC
            """
        ),
        "vip_attendees": fetch_all(
            """
            SELECT DISTINCT a.full_name, a.email, e.event_name
            FROM attendees a
            JOIN tickets t ON a.attendee_id = t.attendee_id
            JOIN events e ON t.event_id = e.event_id
            WHERE t.ticket_type = %s
            ORDER BY a.full_name ASC, e.event_name ASC
            """,
            ("VIP",),
        ),
        "revenue_by_event": fetch_all(
            """
            SELECT
                e.event_name,
                COALESCE(SUM(p.amount_paid), 0) AS total_revenue
            FROM events e
            LEFT JOIN tickets t ON e.event_id = t.event_id
            LEFT JOIN purchases p ON t.ticket_id = p.ticket_id
            GROUP BY e.event_id, e.event_name
            ORDER BY total_revenue DESC, e.event_name ASC
            """
        ),
        "summary_view": fetch_all(
            """
            SELECT
                event_id,
                event_name,
                total_tickets,
                active_tickets,
                vip_tickets,
                total_revenue
            FROM event_ticket_summary
            ORDER BY event_id ASC
            """
        ),
        "above_average_revenue": fetch_all(
            """
            SELECT event_name, total_revenue
            FROM event_ticket_summary
            WHERE total_revenue > (
                SELECT AVG(total_revenue) FROM event_ticket_summary
            )
            ORDER BY total_revenue DESC, event_name ASC
            """
        ),
        "ticket_details": fetch_all(
            """
            SELECT
                t.ticket_id,
                e.event_name,
                a.full_name,
                t.ticket_type,
                t.status
            FROM tickets t
            JOIN events e ON t.event_id = e.event_id
            JOIN attendees a ON t.attendee_id = a.attendee_id
            ORDER BY e.event_time ASC, a.full_name ASC
            """
        ),
        "active_tickets_only": fetch_all(
            """
            SELECT ticket_id, event_id, attendee_id, ticket_type, status
            FROM tickets
            WHERE status = %s
            ORDER BY ticket_id ASC
            """,
            ("Active",),
        ),
    }

    return render_template("reports.html", reports=report_data)
