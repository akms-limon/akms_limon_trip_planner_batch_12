# Smart Group Trip Planner API

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
