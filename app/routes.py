from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)


@main_bp.get('/health')
def health():
    return {"status": "OK"}, 200