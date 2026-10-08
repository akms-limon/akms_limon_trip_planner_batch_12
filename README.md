# Trip Planner API

A REST API for managing group trips, travelers, expenses, and trip status. Built with Python, Flask, Flask-SQLAlchemy, and SQLite.

## 1. Project Overview and Problem Statement

**Problem.** Organizing a group trip involves tracking who has joined, how many seats are left, whether a person is already booked on another trip at the same time, and whether spending is within budget. Done by hand, this leads to overbooking, duplicate sign-ups, clashing trips, and overspending.

**Solution.** This API stores trips, travelers, and expenses, and enforces these rules automatically. It rejects overbooking, duplicate travelers, overlapping trips, overspending, and invalid status changes, and it controls each trip through a defined lifecycle (`PLANNED`, `ONGOING`, `COMPLETED`, `CANCELLED`).

## 2. Prerequisites

- Python 3
- `python3-venv`
- Git

On Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-venv git
```

## 3. Run from a Fresh Clone (`./run.sh`)

```bash
git clone https://github.com/akms-limon/akms_limon_trip_planner_batch_12.git
cd akms_limon_trip_planner_batch_12
./run.sh
```

The script creates or reuses a virtual environment, installs dependencies from `requirements.txt`, initializes the SQLite database when required, and starts the API on `127.0.0.1:5000`.

Verify:

```bash
curl http://127.0.0.1:5000/health
```

```json
{
  "status": "ok"
}
```

## 4. Manual Run Instructions

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

## 5. API Endpoints

**Health**

| Method | Route | Description |
| ------ | ----- | ----------- |
| GET | `/health` | Check application health |

**Trips**

| Method | Route | Description |
| ------ | ----- | ----------- |
| POST | `/api/v1/trips` | Create a trip |
| GET | `/api/v1/trips` | List all trips |
| GET | `/api/v1/trips/<trip_id>` | Retrieve a trip |
| PUT | `/api/v1/trips/<trip_id>` | Update a trip |
| DELETE | `/api/v1/trips/<trip_id>` | Delete a trip |

**Travelers**

| Method | Route | Description |
| ------ | ----- | ----------- |
| POST | `/api/v1/trips/<trip_id>/travelers` | Add a traveler to a trip |
| DELETE | `/api/v1/trips/<trip_id>/travelers/<traveler_id>` | Remove a traveler from a trip |

**Expenses and trip summary**

| Method | Route | Description |
| ------ | ----- | ----------- |
| POST | `/api/v1/trips/<trip_id>/expenses` | Add an expense |
| GET | `/api/v1/trips/<trip_id>/summary` | Get trip summary |

**Trip status**

| Method | Route | Description |
| ------ | ----- | ----------- |
| PATCH | `/api/v1/trips/<trip_id>/status` | Update trip status |


Status codes: `200` success, `201` created, `400` invalid data, `404` not found, `409` business-rule conflict.

## 6. Example Requests and Responses

### Create a trip

```bash
curl -X POST http://127.0.0.1:5000/api/v1/trips \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Cox Bazar",
    "start_date": "2026-10-20",
    "end_date": "2026-10-23",
    "budget": 30000,
    "max_travelers": 5
  }'
```

Response `201`:

```json
{
  "id": 1,
  "destination": "Cox Bazar",
  "start_date": "2026-10-20",
  "end_date": "2026-10-23",
  "budget": 30000,
  "max_travelers": 5,
  "status": "PLANNED"
}
```

### Retrieve a trip

```bash
curl http://127.0.0.1:5000/api/v1/trips/1
```

Response `200`: the trip object shown above.

### List all trips

```bash
curl http://127.0.0.1:5000/api/v1/trips
```

Response `200`: a JSON list of trip objects.

### Update a trip

```bash
curl -X PUT http://127.0.0.1:5000/api/v1/trips/1 \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Cox Bazar",
    "start_date": "2026-10-20",
    "end_date": "2026-10-23",
    "budget": 35000,
    "max_travelers": 6
  }'
```

Response `200`: the updated trip object.

### Add a traveler

```bash
curl -X POST http://127.0.0.1:5000/api/v1/trips/1/travelers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ayesha Rahman",
    "email": "ayesha@example.com"
  }'
```

Response `201`:

```json
{
  "id": 1,
  "name": "Ayesha Rahman",
  "email": "ayesha@example.com"
}
```

### Remove a traveler

```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/trips/1/travelers/1
```

Response `200`:

```json
{
  "message": "Traveler removed successfully"
}
```

### Add an expense

```bash
curl -X POST http://127.0.0.1:5000/api/v1/trips/1/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Hotel",
    "amount": 12000
  }'
```

Response `201`:

```json
{
  "id": 1,
  "title": "Hotel",
  "amount": 12000
}
```

### Update trip status

```bash
curl -X PATCH http://127.0.0.1:5000/api/v1/trips/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ONGOING"
  }'
```

Response `200`:

```json
{
  "id": 1,
  "status": "ONGOING"
}
```

### Get trip summary

```bash
curl http://127.0.0.1:5000/api/v1/trips/1/summary
```

Response `200`:

```json
{
  "trip_id": 1,
  "destination": "Cox Bazar",
  "start_date": "2026-10-20",
  "end_date": "2026-10-23",
  "budget": 30000,
  "max_travelers": 5,
  "status": "ONGOING",
  "traveler_count": 1,
  "available_seats": 4,
  "total_expense": 12000,
  "remaining_budget": 18000
}
```

### Delete a trip

```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/trips/1
```

Response `200`:

```json
{
  "message": "Trip deleted successfully"
}
```

### Example error response

Adding an expense that exceeds the remaining budget returns `409`:

```json
{
  "error": "BUDGET_EXCEEDED",
  "message": "The expense would exceed the trip budget."
}
```

## 7. Business Rules and Assumptions

### Business rules

- The trip end date must be later than the start date.
- Budget and maximum traveler capacity must be positive.
- A traveler cannot join the same trip more than once, based on email.
- A trip cannot exceed its maximum traveler capacity.
- A traveler cannot join trips with overlapping date ranges. Back-to-back trips are allowed when the first trip ends before the second begins.
- Expense amounts must be positive.
- Total expenses cannot exceed the trip budget. Spending exactly the remaining budget is allowed.
- Maximum capacity cannot be reduced below the current traveler count.
- Travelers can be added only while a trip is `PLANNED`.
- Expenses can be added only while a trip is `PLANNED` or `ONGOING`.
- `COMPLETED` and `CANCELLED` trips cannot be edited or accept travelers or expenses.
- `COMPLETED` and `CANCELLED` trips cannot transition to another status.

### Allowed status transitions

- `PLANNED` → `ONGOING`
- `ONGOING` → `COMPLETED`
- `PLANNED` → `CANCELLED`
- `ONGOING` → `CANCELLED`

All other transitions are rejected with `409`.

### Assumptions

- A traveler is identified by email address.
- Traveler email addresses are normalized to lowercase before being stored.
- Dates use the `YYYY-MM-DD` format.
- A new trip starts with the status `PLANNED`.
- The API is used by a single local client; there is no authentication.

## 8. Project Structure

```text
akms_limon_trip_planner_batch_12/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── errors.py
│   ├── models.py
│   ├── routes.py
│   ├── services.py
│   ├── utils.py
│   └── validators.py
├── tests/
│   └── test_services.py
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
└── run.sh
```

## 9. SQLite Initialization and Storage

- Flask-SQLAlchemy manages the models and relationships for trips, travelers, and expenses.
- Tables are created automatically when the application starts, so no manual SQL setup is needed.
- The database file is stored at `instance/trip_planner.db`.
- It is generated locally and is not committed to the repository.
- Data is stored in SQLite, not in memory, so it persists across restarts.

## 10. Known Limitations

- No authentication or authorization.
- No frontend; REST API only.
- Uses a local SQLite database only; no external database support.
- Intended to run locally on `127.0.0.1:5000`; no deployment configuration.
```