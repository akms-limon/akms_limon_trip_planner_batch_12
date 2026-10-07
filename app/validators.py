from datetime import date


def validate_trip_data(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    required_fields = [
        "destination",
        "start_date",
        "end_date",
        "budget",
        "max_travelers",
    ]

    for field in required_fields:
        if field not in data:
            return None, f"Missing required field: {field}"

    destination = data["destination"]
    if not isinstance(destination, str) or not destination.strip():
        return None, "Destination must be a non-empty string"

    try:
        start_date = date.fromisoformat(data["start_date"])
        end_date = date.fromisoformat(data["end_date"])
    except (ValueError, TypeError):
        return None, "Dates must use YYYY-MM-DD format"

    if end_date < start_date:
        return None, "End date must be later than start date"

    budget = data["budget"]
    if (
        isinstance(budget, bool)
        or not isinstance(budget, (int, float))
        or budget <= 0
    ):
        return None, "Budget must be a positive number"

    max_travelers = data["max_travelers"]
    if (
        isinstance(max_travelers, bool)
        or not isinstance(max_travelers, int)
        or max_travelers <= 0
    ):
        return None, "Max travelers must be a positive integer"

    cleaned_data = {
        "destination": destination.strip(),
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "max_travelers": max_travelers,
    }

    return cleaned_data, None


def validate_traveler_data(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    if "name" not in data:
        return None, "Missing required field: name"

    if "email" not in data:
        return None, "Missing required field: email"

    name = data["name"]
    email = data["email"]

    if not isinstance(name, str) or not name.strip():
        return None, "Name must be a non-empty string"

    if not isinstance(email, str) or not email.strip():
        return None, "Email must be a non-empty string"

    cleaned_data = {
        "name": name.strip(),
        "email": email.strip().lower(),
    }

    return cleaned_data, None


def validate_expense_data(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    if "title" not in data:
        return None, "Missing required field: title"

    if "amount" not in data:
        return None, "Missing required field: amount"

    title = data["title"]
    amount = data["amount"]

    if not isinstance(title, str) or not title.strip():
        return None, "Title must be a non-empty string"

    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or amount <= 0:
        return None, "Amount must be a positive number"

    cleaned_data = {
        "title": title.strip(),
        "amount": amount,
    }

    return cleaned_data, None