
from app import db
from app.models import Trip, Traveler, Expense


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


def update_trip(trip, data):
    if trip.status in ["COMPLETED", "CANCELLED"]:
        return (
            None,
            "TRIP_NOT_EDITABLE",
            f"{trip.status} trips cannot be edited.",
        )

    if data["max_travelers"] < len(trip.travelers):
        return (
            None,
            "CAPACITY_TOO_LOW",
            "Max travelers cannot be less than the current traveler count.",
        )

    total_expenses = sum(expense.amount for expense in trip.expenses)

    if data["budget"] < total_expenses:
        return (
            None,
            "BUDGET_TOO_LOW",
            "Budget cannot be less than the total expenses.",
        )

    trip.destination = data["destination"]
    trip.start_date = data["start_date"]
    trip.end_date = data["end_date"]
    trip.budget = data["budget"]
    trip.max_travelers = data["max_travelers"]

    db.session.commit()

    return trip, None, None


def delete_trip(trip):
    db.session.delete(trip)
    db.session.commit()


def add_traveler(trip, data):
    if trip.status != "PLANNED":
        return None, "TRIP_NOT_PLANNED", "Travelers can only be added to planned trips."

    if len(trip.travelers) >= trip.max_travelers:
        return None, "TRIP_FULL", "The trip has reached its maximum traveler capacity."

    traveler = Traveler.query.filter_by(email=data["email"]).first()

    if traveler and traveler in trip.travelers:
        return None, "DUPLICATE_TRAVELER", "The traveler is already part of this trip."

    if traveler:
        for existing_trip in traveler.trips:
            if (
                existing_trip.start_date < trip.end_date
                and existing_trip.end_date > trip.start_date
            ):
                return (
                    None,
                    "TRIP_OVERLAP",
                    "The traveler already has another trip during these dates.",
                )

    if not traveler:
        traveler = Traveler(
            name=data["name"],
            email=data["email"],
        )
        db.session.add(traveler)

    trip.travelers.append(traveler)
    db.session.commit()

    return traveler, None, None


def get_traveler_by_id(traveler_id):
    return db.session.get(Traveler, traveler_id)




def remove_traveler(trip, traveler_id):
    if trip.status != "PLANNED":
        return (
            None,
            "TRIP_NOT_PLANNED",
            "Travelers can only be removed from planned trips.",
        )

    traveler = db.session.get(Traveler, traveler_id)

    if not traveler:
        return None, "TRAVELER_NOT_FOUND", "Traveler not found."

    if traveler not in trip.travelers:
        return None, "TRAVELER_NOT_IN_TRIP", "The traveler is not part of this trip."

    trip.travelers.remove(traveler)
    db.session.commit()

    return traveler, None, None


def add_expense(trip, data):
    if trip.status not in ["PLANNED", "ONGOING"]:
        return (
            None,
            "TRIP_NOT_ACTIVE",
            "Expenses can only be added to planned or ongoing trips.",
        )

    total_expenses = sum(expense.amount for expense in trip.expenses)

    if total_expenses + data["amount"] > trip.budget:
        return (
            None,
            "BUDGET_EXCEEDED",
            "The expense would exceed the trip budget.",
        )

    expense = Expense(
        trip_id=trip.id,
        title=data["title"],
        amount=data["amount"],
    )

    db.session.add(expense)
    db.session.commit()

    return expense, None, None


def get_trip_summary(trip):
    traveler_count = len(trip.travelers)
    available_seats = trip.max_travelers - traveler_count
    total_expense = sum(expense.amount for expense in trip.expenses)
    remaining_budget = trip.budget - total_expense

    return {
        "trip_id": trip.id,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "budget": trip.budget,
        "max_travelers": trip.max_travelers,
        "status": trip.status,
        "traveler_count": traveler_count,
        "available_seats": available_seats,
        "total_expense": total_expense,
        "remaining_budget": remaining_budget,
    }


def update_trip_status(trip, new_status):
    allowed_transitions = {
        "PLANNED": ["ONGOING", "CANCELLED"],
        "ONGOING": ["COMPLETED", "CANCELLED"],
        "COMPLETED": [],
        "CANCELLED": [],
    }

    if new_status not in allowed_transitions[trip.status]:
        return (
            None,
            "INVALID_STATUS_TRANSITION",
            f"Cannot change status from {trip.status} to {new_status}.",
        )

    trip.status = new_status
    db.session.commit()

    return trip, None, None