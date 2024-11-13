from flask import Blueprint

warehouse_bp = Blueprint("warehouse", __name__, template_folder="templates")

from . import routes