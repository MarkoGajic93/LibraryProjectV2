from flask import Blueprint

author_bp = Blueprint("author", __name__, template_folder="templates")

from . import routes