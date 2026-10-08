import pytest

from app import create_app, db
from app.models import Trip, Traveler, Expense
from app.services import (
    create_trip,
    get_all_trips,
    get_trip_by_id,
    update_trip,
    delete_trip,
    add_traveler,
    get_traveler_by_id,
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


def test_add_traveler(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        traveler, error_code, error_message = add_traveler(
            trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert traveler is not None
        assert traveler.name == "Limon"
        assert traveler.email == "limon@example.com"
        assert error_code is None
        assert error_message is None
        assert traveler in trip.travelers


def test_add_traveler_to_non_planned_trip(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        trip.status = "ONGOING"
        db.session.commit()

        traveler, error_code, error_message = add_traveler(
            trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert traveler is None
        assert error_code == "TRIP_NOT_PLANNED"
        assert error_message == "Travelers can only be added to planned trips."


def test_add_traveler_to_full_trip(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 1,
        })

        traveler, error_code, error_message = add_traveler(
            trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert error_code is None

        traveler, error_code, error_message = add_traveler(
            trip,
            {
                "name": "Rahim",
                "email": "rahim@example.com",
            },
        )

        assert traveler is None
        assert error_code == "TRIP_FULL"
        assert error_message == "The trip has reached its maximum traveler capacity."


def test_add_duplicate_traveler(app):
    with app.app_context():
        trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        traveler_data = {
            "name": "Limon",
            "email": "limon@example.com",
        }

        traveler, error_code, error_message = add_traveler(
            trip,
            traveler_data,
        )

        assert error_code is None

        traveler, error_code, error_message = add_traveler(
            trip,
            traveler_data,
        )

        assert traveler is None
        assert error_code == "DUPLICATE_TRAVELER"
        assert error_message == "The traveler is already part of this trip."


def test_add_traveler_with_overlapping_trip(app):
    with app.app_context():
        first_trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        traveler, error_code, error_message = add_traveler(
            first_trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert error_code is None

        second_trip = create_trip({
            "destination": "Sylhet",
            "start_date": date(2026, 10, 22),
            "end_date": date(2026, 10, 25),
            "budget": 40000,
            "max_travelers": 5,
        })

        traveler, error_code, error_message = add_traveler(
            second_trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert traveler is None
        assert error_code == "TRIP_OVERLAP"
        assert error_message == "The traveler already has another trip during these dates."


def test_add_existing_traveler_to_non_overlapping_trip(app):
    with app.app_context():
        first_trip = create_trip({
            "destination": "Cox Bazar",
            "start_date": date(2026, 10, 20),
            "end_date": date(2026, 10, 23),
            "budget": 30000,
            "max_travelers": 5,
        })

        traveler, error_code, error_message = add_traveler(
            first_trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert error_code is None

        second_trip = create_trip({
            "destination": "Sylhet",
            "start_date": date(2026, 10, 23),
            "end_date": date(2026, 10, 25),
            "budget": 40000,
            "max_travelers": 5,
        })

        traveler, error_code, error_message = add_traveler(
            second_trip,
            {
                "name": "Limon",
                "email": "limon@example.com",
            },
        )

        assert traveler is not None
        assert error_code is None
        assert error_message is None
        assert traveler in second_trip.travelers


def test_get_traveler_by_id(app):
    with app.app_context():
        traveler = Traveler(
            name="Limon",
            email="limon@example.com",
        )

        db.session.add(traveler)
        db.session.commit()

        found_traveler = get_traveler_by_id(traveler.id)

        assert found_traveler is not None
        assert found_traveler.id == traveler.id
        assert found_traveler.name == "Limon"
        assert found_traveler.email == "limon@example.com"


def test_get_traveler_by_id_not_found(app):
    with app.app_context():
        traveler = get_traveler_by_id(999)

        assert traveler is None