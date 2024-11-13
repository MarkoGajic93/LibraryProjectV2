import uuid

from flask import render_template, flash, url_for, abort, g, current_app
from werkzeug.utils import redirect

from app import db
from app.auth.routes import is_admin, get_current_user
from app.book import book_bp
from app.book.forms import NewBookForm, DeleteAllBooksForm, EditBookWarehouseCopies, RentBookForm
from app.db_models import Book, WarehouseBook
from db.db_service import get_db


@book_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin():
        abort(401)

    form = _setup_form()

    if form.validate_on_submit():
        # Check if book already exist
        # (NOTE: criteria - books with same title, author and publish year are the same books, with same id)
        book_id = (Book.query.with_entities(Book.id).
                   filter_by(title=form.title.data, year_published=form.year_published.data, author_id=form.author.data).first())

        # If not found - insert new record
        if not book_id:
            book = Book(title=form.title.data, year_published=form.year_published.data, author_id=form.author.data)
            db.session.add(book)
            db.session.flush()
            warehouse_book = WarehouseBook(form.warehouse.data, book.id, form.quantity.data)
            db.session.add(warehouse_book)
            db.session.commit()

        # If found - no interaction with the book table, just update quantity in the warehouse
        else:
            warehouse_book = WarehouseBook.query.filter_by(warehouse_id=form.warehouse.data, book_id=book_id).first()
            # Check if book already have some copies in the selected warehouse
            if warehouse_book:
                warehouse_book.quantity = warehouse_book.quantity+form.quantity.data
            # If it doesn't, create new warehouse_book
            else:
                warehouse_book = WarehouseBook(form.warehouse.data, book_id, form.quantity.data)
            db.session.add(warehouse_book)
            db.session.commit()
        flash(f"Book: {form.title.data.upper()} added successfully.", "success")
        return redirect(url_for("home.home"))

    return render_template("new_book.html", form=form)

def _setup_form() -> NewBookForm:
    form = NewBookForm()
    form.set_choices("Author")
    form.set_choices("Warehouse")
    return form

@book_bp.route("/<uuid:book_id>")
def book(book_id: uuid.UUID):
    conn = get_db()
    cursor = conn.cursor()
    delete_all_books_form = DeleteAllBooksForm()
    rent_book_form = RentBookForm()

    book_data = get_book_data(cursor, book_id)
    book_dict = {}
    if book_data:
        book_dict = next(iter(generate_book_dict(book_data).values()))
        return render_template("book.html",
                               book=book_dict,
                               deleteAllBooksForm=delete_all_books_form,
                               rentBookForm=rent_book_form)
    else:
        flash("That book doesnt exist", "danger")
        return redirect(url_for("home.home"))

@book_bp.route("/edit/<uuid:book_id>", methods=["GET", "POST"])
def manage_copies(book_id: uuid.UUID):
    if not is_admin():
        abort(401)

    conn = get_db()
    cursor = conn.cursor()

    book_data = get_book_data(cursor, book_id)
    book_dict = {}
    if book_data:
        edit_form = EditBookWarehouseCopies()
        book_dict = next(iter(generate_book_dict(book_data).values()))
        cursor.execute("""SELECT id, name FROM warehouse""")
        warehouses = cursor.fetchall()
        edit_form.warehouse.choices = warehouses

        if edit_form.validate_on_submit():
            selected_warehouse = next((warehouse[1] for warehouse in warehouses if warehouse[0] == edit_form.warehouse.data))

            if edit_form.quantity.data == 0:
                cursor.execute("""DELETE FROM warehouse_book WHERE warehouse_id=%s AND book_id=%s""",
                               (edit_form.warehouse.data, book_dict["id"]))
                if not get_book_data(cursor, book_dict["id"]):
                    cursor.execute("""DELETE FROM book WHERE id=%s""", (book_dict["id"],))

            if selected_warehouse in book_dict["warehouses"].keys():
                cursor.execute("""UPDATE warehouse_book SET quantity=%s WHERE warehouse_id=%s AND book_id=%s""",
                               (edit_form.quantity.data, edit_form.warehouse.data, book_dict["id"]))

            else:
                cursor.execute("""INSERT INTO warehouse_book (warehouse_id, book_id, quantity) VALUES (%s,%s,%s)""",
                               (edit_form.warehouse.data, book_dict["id"], edit_form.quantity.data))

            conn.commit()
            flash(f"Book {book_dict['title']} updated successfully.", "success")
            return redirect(url_for('book.book', book_id=book_id))

        return render_template("edit_copies.html", book=book_dict, editForm=edit_form)

    else:
        flash("That book doesnt exist", "danger")
        return redirect(url_for("home.home"))

def get_book_data(book_id=None) -> list[Book]:
    if book_id:
        book = Book.query.filter_by(id=book_id)
        return list(book)
    return Book.query.all()

@book_bp.route("/delete_all/<uuid:book_id>", methods=["POST"])
def delete_all(book_id: uuid.UUID):
    if not is_admin():
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, title FROM book WHERE id=%s""", (str(book_id),))
    book_db_id, title = cursor.fetchone()
    if book_db_id:
        cursor.execute("""DELETE FROM book WHERE id=%s""", (book_db_id,))
        conn.commit()
        flash(f"Book {title} deleted successfully from all warehouses.", "success")
    else:
        flash(f"Book {title} doesnt exist.", "danger")
    return redirect(url_for("home.home"))

