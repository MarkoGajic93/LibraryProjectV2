from flask import render_template

from db.db_service import get_db
from . import home_bp
from ..book.routes import get_book_data, generate_book_dict


@home_bp.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor()
    books_data = get_book_data(cursor)
    book_dicts = {}
    if books_data:
        book_dicts.update(generate_book_dict(books_data))

    books = list(book_dicts.values())

    return render_template("home.html", books=books)


