-- Expected error: duplicate key value violates unique constraint on attendees.email
INSERT INTO attendees (full_name, email, phone)
VALUES ('Duplicate Email', 'maya.chen@example.com', '555-000-0000');

-- Expected error: new row for relation "tickets" violates check constraint on ticket_type
INSERT INTO tickets (event_id, attendee_id, ticket_type, privilege, origin, status)
VALUES (1, 3, 'Premium', 'Invalid type example', 'Online', 'Active');

-- Expected error: Cannot add another active ticket. Event 3 is already at capacity.
INSERT INTO tickets (event_id, attendee_id, ticket_type, privilege, origin, status)
VALUES (3, 2, 'General', 'Should fail because capacity is zero', 'Walk-in', 'Active');
