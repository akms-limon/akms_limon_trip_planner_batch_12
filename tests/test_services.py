import pytest

from app import create_app, db
from app.models import Trip, Traveler, Expense
from app.services import (
    create_trip,
    get_all_trips,
    get_trip_by_id,
    update_trip,
    delete_trip
)
from datetime import date


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()


def test_create_trip(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        assert trip.id is not None
        assert trip.destination == "Cox Bazar"
        assert trip.budget == 30000
        assert trip.max_travelers == 5
        assert trip.status == "PLANNED"

        saved_trip = db.session.get(Trip, trip.id)

        assert saved_trip is not None


def test_get_all_trips(app):
    with app.app_context():
        create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        create_trip({
            "destination": "Sylhet",
            "start_date": date(2026, 11, 1),
            "end_date": date(2026, 11, 4),
            "budget": 40000,
            "max_travelers": 4,
        })

        trips = get_all_trips()

        assert len(trips) == 2
        assert trips[0].destination == "Cox Bazar"
        assert trips[1].destination == "Sylhet"


def test_get_trip_by_id(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        found_trip = get_trip_by_id(trip.id)

        assert found_trip is not None
        assert found_trip.id == trip.id
        assert found_trip.destination == "Cox Bazar"

def test_get_trip_by_id_not_found(app):
    with app.app_context():
        trip = get_trip_by_id(999)

        assert trip is None


def test_update_trip(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        updated_trip, error_code, error_message = update_trip(trip, {
            "destination": "Sylhet",
            "start_date": date(2026, 11, 1),
            "end_date": date(2026, 11, 4),
            "budget": 40000,
            "max_travelers": 6,
        })

        assert error_code is None
        assert error_message is None
        assert updated_trip.destination == "Sylhet"
        assert updated_trip.budget == 40000
        assert updated_trip.max_travelers == 6

def test_update_completed_or_cancelled_trip(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        for status in ["COMPLETED", "CANCELLED"]:
            trip.status = status
            db.session.commit()

            updated_trip, error_code, error_message = update_trip(trip, {
                "destination": "Sylhet",
                "start_date": date(2026, 11, 1),
                "end_date": date(2026, 11, 4),
                "budget": 40000,
                "max_travelers": 6,
            })

            assert updated_trip is None
            assert error_code == "TRIP_NOT_EDITABLE"
            assert error_message == f"{status} trips cannot be edited."


def test_update_trip_capacity_too_low(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        traveler = Traveler(
            name="Limon",
            email="limon@example.com",
        )

        trip.travelers.append(traveler)
        db.session.commit()

        updated_trip, error_code, error_message = update_trip(trip, {
            "destination": "Sylhet",
            "start_date": date(2026, 11, 1),
            "end_date": date(2026, 11, 4),
            "budget": 40000,
            "max_travelers": 0,
        })

        assert updated_trip is None
        assert error_code == "CAPACITY_TOO_LOW"
        assert error_message == "Max travelers cannot be less than the current traveler count."


def test_update_trip_budget_too_low(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        expense = Expense(
            trip_id=trip.id,
            title="Hotel",
            amount=20000,
        )

        db.session.add(expense)
        db.session.commit()

        updated_trip, error_code, error_message = update_trip(trip, {
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 15000,
            "max_travelers": 5,
        })

        assert updated_trip is None
        assert error_code == "BUDGET_TOO_LOW"
        assert error_message == "Budget cannot be less than the total expenses."

def test_delete_trip(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        trip_id = trip.id

        delete_trip(trip)

        deleted_trip = db.session.get(Trip, trip_id)

        assert deleted_trip is None