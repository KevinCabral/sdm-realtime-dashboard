# Real-Time Election Turnout Dashboard

Operational Plotly Dash application for near real-time election turnout monitoring.

> This system is only for election operations (voted / not voted / pending validation). It does not track political preference, voting choices, religion, ethnicity, or political opinions.

## Features

- Responsive Plotly Dash + Dash Bootstrap Components UI
- Auto-refresh every 5 seconds (`dcc.Interval`)
- Simulated turnout updates using Pandas
- KPIs:
  - Total registered voters
  - Total voted
  - Total not voted
  - Turnout percentage
- Charts:
  - Votes by polling station
  - Votes by region/municipality
  - Hourly voting trend
- Search and filters:
  - Polling station
  - Region
  - Voting status
  - Text search by voter name/ID
- Voter table with required fields
- Last update timestamp, loading indicators, and error handling
- Authentication and RBAC placeholders
- Audit logging of data access events
- Environment-based configuration ready for secure integration

## Project Structure

- `app.py`
- `requirements.txt`
- `.env`
- `README.md`
- `Dockerfile`
- `docker-compose.yml`
- `assets/`
- `pages/`
- `components/`
- `services/`
- `data/`

## Architecture

`Nginx → Gunicorn → Dash App → Service Layer → PostgreSQL/API/CSV`

Current implementation uses CSV + Pandas simulation and is prepared for future service-layer integrations with:

- PostgreSQL (`POSTGRES_URI`)
- REST API (`REST_API_BASE_URL`)
- CSV upload path (`CSV_DATA_PATH`)
- Real-time backend strategy (`REALTIME_BACKEND`, e.g., WebSocket/Redis)

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:8050`.

## Run with Docker Compose

```bash
docker compose up --build
```

Open `http://localhost:8080` (Nginx proxy).
