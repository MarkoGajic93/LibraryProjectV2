from flask import render_template

from . import home_bp
from ..db_models import Book


@home_bp.route("/")
def home():
    books = Book.query.all()

    return render_template("home.html", books=books)


