from flask import render_template

from db.db_service import get_db
from . import home_bp
from ..book.routes import get_book_data


@home_bp.route("/")
def home():
    books = get_book_data()

    return render_template("home.html", books=books)


