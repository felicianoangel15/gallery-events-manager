DROP VIEW IF EXISTS event_ticket_summary;
DROP TRIGGER IF EXISTS check_event_capacity_trigger ON tickets;
DROP FUNCTION IF EXISTS check_event_capacity();
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS attendees;
DROP TABLE IF EXISTS events;

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    event_name VARCHAR(150) NOT NULL,
    event_location VARCHAR(150) NOT NULL,
    event_time TIMESTAMP NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 0),
    ticket_price NUMERIC(10, 2) NOT NULL CHECK (ticket_price >= 0)
);

CREATE TABLE attendees (
    attendee_id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(25)
);

CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES events(event_id),
    attendee_id INTEGER NOT NULL REFERENCES attendees(attendee_id),
    ticket_type VARCHAR(20) NOT NULL CHECK (ticket_type IN ('VIP', 'General', 'Student')),
    privilege VARCHAR(100),
    origin VARCHAR(100),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Active', 'Used', 'Cancelled'))
);

CREATE TABLE purchases (
    purchase_id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL UNIQUE REFERENCES tickets(ticket_id),
    purchase_date DATE NOT NULL,
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('Card', 'Cash', 'Online', 'Complimentary')),
    amount_paid NUMERIC(10, 2) NOT NULL CHECK (amount_paid >= 0)
);

CREATE OR REPLACE FUNCTION check_event_capacity()
RETURNS TRIGGER AS $$
DECLARE
    current_active_count INTEGER;
    allowed_capacity INTEGER;
BEGIN
    IF NEW.status <> 'Active' THEN
        RETURN NEW;
    END IF;

    SELECT capacity
    INTO allowed_capacity
    FROM events
    WHERE event_id = NEW.event_id;

    SELECT COUNT(*)
    INTO current_active_count
    FROM tickets
    WHERE event_id = NEW.event_id
      AND status = 'Active'
      AND (TG_OP = 'INSERT' OR ticket_id <> NEW.ticket_id);

    IF current_active_count >= allowed_capacity THEN
        RAISE EXCEPTION 'Cannot add another active ticket. Event % is already at capacity.', NEW.event_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_event_capacity_trigger
BEFORE INSERT OR UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION check_event_capacity();

CREATE VIEW event_ticket_summary AS
SELECT
    e.event_id,
    e.event_name,
    COUNT(t.ticket_id) AS total_tickets,
    COUNT(*) FILTER (WHERE t.status = 'Active') AS active_tickets,
    COUNT(*) FILTER (WHERE t.ticket_type = 'VIP') AS vip_tickets,
    COALESCE(SUM(p.amount_paid), 0) AS total_revenue
FROM events e
LEFT JOIN tickets t ON e.event_id = t.event_id
LEFT JOIN purchases p ON t.ticket_id = p.ticket_id
GROUP BY e.event_id, e.event_name;
