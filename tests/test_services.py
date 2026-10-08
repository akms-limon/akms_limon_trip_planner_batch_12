import pytest

from app import create_app, db
from app.models import Trip
from app.services import create_trip, get_all_trips
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