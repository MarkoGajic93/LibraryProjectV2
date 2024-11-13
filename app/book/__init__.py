from flask import Blueprint

book_bp = Blueprint("book", __name__, template_folder="templates")

from . import routes