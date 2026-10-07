
from app import db
from app.models import Trip


def create_trip(data):
    trip = Trip(
        destination=data["destination"],
        start_date=data["start_date"],
        end_date=data["end_date"],
        budget=data["budget"],
        max_travelers=data["max_travelers"],
    )

    db.session.add(trip)
    db.session.commit()

    return trip

def get_all_trips():
    return Trip.query.all()

def get_trip_by_id(trip_id):
    return db.session.get(Trip, trip_id)