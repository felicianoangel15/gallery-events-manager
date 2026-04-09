INSERT INTO events (event_name, event_location, event_time, capacity, ticket_price) VALUES
('Spring Student Showcase', 'Downtown Gallery Hall', '2026-05-15 18:00:00', 120, 20.00),
('Sculpture Night', 'Riverside Exhibit Loft', '2026-06-01 19:30:00', 80, 35.00),
('Photography Open House', 'Campus Art Annex', '2026-04-20 17:00:00', 0, 0.00),
('Alumni Curator Talk', 'Museum Lecture Room', '2026-04-12 14:00:00', 60, 15.00);

INSERT INTO attendees (full_name, email, phone) VALUES
('Maya Chen', 'maya.chen@example.com', '555-111-2222'),
('Jordan Smith', 'jordan.smith@example.com', NULL),
('Priya Patel', 'priya.patel@example.com', '555-333-4444'),
('Leo Martinez', 'leo.martinez@example.com', '555-444-5555'),
('Ava Johnson', 'ava.johnson@example.com', NULL);

INSERT INTO tickets (event_id, attendee_id, ticket_type, privilege, origin, status) VALUES
(1, 1, 'VIP', 'Backstage preview access', 'Instagram campaign', 'Active'),
(1, 2, 'General', 'Standard access', 'Walk-in', 'Used'),
(2, 3, 'Student', 'Student discount', 'Online', 'Active'),
(4, 4, 'VIP', 'Artist meet-and-greet', 'Sponsor list', 'Active'),
(4, 5, 'General', NULL, 'Online', 'Cancelled'),
(2, 2, 'General', 'Standard access', 'Walk-in', 'Active');

INSERT INTO purchases (ticket_id, purchase_date, payment_method, amount_paid) VALUES
(1, '2026-03-20', 'Card', 20.00),
(2, '2026-03-22', 'Cash', 20.00),
(3, '2026-03-28', 'Card', 15.00),
(4, '2026-04-01', 'Online', 15.00),
(5, '2026-04-02', 'Card', 15.00);
