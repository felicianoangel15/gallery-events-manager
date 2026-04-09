# Gallery Events Manager

## Start

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Database

Make sure PostgreSQL is running, then create the database:

```sql
CREATE DATABASE gallery_events_manager;
```

Load the schema and sample data:

```bash
psql -U postgres -d gallery_events_manager -f db_proof/schema.sql
psql -U postgres -d gallery_events_manager -f db_proof/data.sql
```

Update `.env` if your PostgreSQL user, password, host, or port are different.

## Run

```bash
cd backend
python app.py
```

Open `http://127.0.0.1:5000`
