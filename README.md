# Gallery Events Manager

Gallery Events Manager is a simple full-stack student database project built with Flask, PostgreSQL, Jinja templates, and vanilla JavaScript. It is designed to be easy to study, run locally, and modify for a class final project.

## Features

- CRUD workflow for events
- Add and list attendees
- Create and list tickets
- Create and list purchases
- Dashboard with summary cards
- Reports page showing SQL query results
- PostgreSQL view: `event_ticket_summary`
- PostgreSQL trigger that prevents active ticket sales beyond event capacity
- Server-side validation and safe parameterized SQL

## Tech Stack

- Backend: Python Flask
- Database: PostgreSQL
- Frontend: HTML, CSS, vanilla JavaScript, Jinja templates
- Database driver: `psycopg2-binary`

## Project Structure

```text
final_project/
  README.md
  report.pdf
  frontend/
  backend/
  db_proof/
  requirements.txt
  .env.example
```

Important folders:

- `backend/app.py`: Flask entry point
- `backend/db.py`: PostgreSQL connection helper
- `backend/routes/main.py`: application routes
- `backend/validators.py`: simple server-side validation
- `backend/templates/`: Jinja templates
- `backend/static/`: CSS and JavaScript
- `db_proof/schema.sql`: tables, constraints, view, trigger, trigger function
- `db_proof/data.sql`: sample records
- `db_proof/constraints_test.sql`: failing test inserts
- `db_proof/queries.sql`: labeled SQL queries
- `db_proof/query_outputs.txt`: sample query results

## Database Setup

1. Make sure PostgreSQL is installed and running.
2. Create a database:

```sql
CREATE DATABASE gallery_events_manager;
```

3. Open the database:

```bash
psql -U postgres -d gallery_events_manager
```

4. Run the schema file:

```bash
\i db_proof/schema.sql
```

5. Load sample data:

```bash
\i db_proof/data.sql
```

Optional proof files:

```bash
\i db_proof/constraints_test.sql
\i db_proof/queries.sql
```

## Python Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Copy the example environment file and update it if needed:

```bash
cp .env.example .env
```

Default variables:

- `SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## Running the Flask App

Move into the backend folder and start Flask:

```bash
cd backend
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Required SQL Coverage in the App

The application executes all major query types through Flask route handlers:

- Basic `SELECT ... WHERE`
- `JOIN`
- `GROUP BY` with aggregate
- `ORDER BY`
- Subquery
- `INSERT`
- `UPDATE`
- `DELETE`

Extra reports also include:

- ticket counts by event
- VIP attendee lookup
- revenue by event
- upcoming events only

## Advanced Database Features

### View

`event_ticket_summary` combines event information with ticket counts and revenue totals:

- `event_id`
- `event_name`
- `total_tickets`
- `active_tickets`
- `vip_tickets`
- `total_revenue`

### Trigger

The trigger `check_event_capacity_trigger` calls `check_event_capacity()` before inserting or updating a ticket.

If a new or updated ticket would make the number of active tickets exceed the event capacity, PostgreSQL raises an error and rejects the change.

## Notes for Study

- This project uses raw SQL instead of an ORM so the database logic stays visible.
- SQL statements are parameterized to avoid SQL injection.
- Validation is intentionally simple and readable for class use.
- The code is organized but not overengineered.
