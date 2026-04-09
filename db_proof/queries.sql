-- Query 1: Basic SELECT with WHERE and ORDER BY
SELECT event_id, event_name, event_location, event_time
FROM events
WHERE event_time >= CURRENT_TIMESTAMP
ORDER BY event_time ASC;

-- Query 2: JOIN across multiple tables
SELECT
    t.ticket_id,
    e.event_name,
    a.full_name,
    t.ticket_type,
    t.status
FROM tickets t
JOIN events e ON t.event_id = e.event_id
JOIN attendees a ON t.attendee_id = a.attendee_id
ORDER BY e.event_time ASC, a.full_name ASC;

-- Query 3: GROUP BY with aggregate
SELECT
    e.event_name,
    COUNT(t.ticket_id) AS total_tickets
FROM events e
LEFT JOIN tickets t ON e.event_id = t.event_id
GROUP BY e.event_id, e.event_name
ORDER BY total_tickets DESC, e.event_name ASC;

-- Query 4: ORDER BY attendees alphabetically
SELECT attendee_id, full_name, email
FROM attendees
ORDER BY full_name ASC;

-- Query 5: Subquery for above-average revenue events
SELECT event_name, total_revenue
FROM event_ticket_summary
WHERE total_revenue > (
    SELECT AVG(total_revenue) FROM event_ticket_summary
)
ORDER BY total_revenue DESC;

-- Query 6: INSERT example
INSERT INTO attendees (full_name, email, phone)
VALUES ('Noah Brooks', 'noah.brooks@example.com', '555-222-8888');

-- Query 7: UPDATE example
UPDATE events
SET ticket_price = 25.00
WHERE event_id = 1;

-- Query 8: DELETE example
DELETE FROM purchases
WHERE purchase_id = 5;

-- Extra Query 9: Count active tickets by event using the view
SELECT event_id, event_name, active_tickets
FROM event_ticket_summary
ORDER BY active_tickets DESC, event_name ASC;

-- Extra Query 10: Find attendees with VIP tickets
SELECT DISTINCT a.full_name, a.email, e.event_name
FROM attendees a
JOIN tickets t ON a.attendee_id = t.attendee_id
JOIN events e ON t.event_id = e.event_id
WHERE t.ticket_type = 'VIP'
ORDER BY a.full_name ASC, e.event_name ASC;

-- Extra Query 11: Total revenue by event
SELECT
    e.event_name,
    COALESCE(SUM(p.amount_paid), 0) AS total_revenue
FROM events e
LEFT JOIN tickets t ON e.event_id = t.event_id
LEFT JOIN purchases p ON t.ticket_id = p.ticket_id
GROUP BY e.event_id, e.event_name
ORDER BY total_revenue DESC, e.event_name ASC;
