from app import db


trip_travelers = db.Table(
    "trip_travelers",
    db.Column("trip_id", db.Integer, db.ForeignKey("trips.id"), primary_key=True),
    db.Column("traveler_id", db.Integer, db.ForeignKey("travelers.id"), primary_key=True),
)


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    max_travelers = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PLANNED")

    travelers = db.relationship(
        "Traveler",
        secondary=trip_travelers,
        back_populates="trips",
    )

    expenses = db.relationship(
        "Expense",
        back_populates="trip",
        cascade="all, delete-orphan",
    )


class Traveler(db.Model):
    __tablename__ = "travelers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)

    trips = db.relationship(
        "Trip",
        secondary=trip_travelers,
        back_populates="travelers",
    )


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    trip = db.relationship(
        "Trip",
        back_populates="expenses"
    )
