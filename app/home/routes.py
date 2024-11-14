from flask import render_template, request

from . import home_bp
from .forms import FilterForm
from ..db_models import Book, Author


@home_bp.route("/")
def home():
    filter_form = FilterForm(request.args, meta={"csrf": False})
    authors = [(author.id, author.name) for author in Author.query.all()]
    authors.insert(0, (0, "---"))
    filter_form.author.choices = authors
    books = Book.query.all()

    if filter_form.validate():
        query = Book.query
        if filter_form.title.data:
            query = query.filter(Book.title.like(f"%{filter_form.title.data.upper()}%"))
        if filter_form.author.data != '0':
            query = query.filter_by(author_id=filter_form.author.data)
        if filter_form.year_published.data == '1':
            query = query.order_by(Book.year_published.desc())
        if filter_form.year_published.data == '2':
            query = query.order_by(Book.year_published.asc())
        books = query.all()

    return render_template("home.html", books=books, form=filter_form)


