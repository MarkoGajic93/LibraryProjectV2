from flask import Blueprint

rent_bp = Blueprint("rent", __name__, template_folder="templates")

from . import routes