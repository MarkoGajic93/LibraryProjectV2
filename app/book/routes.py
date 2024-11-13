import uuid

from flask import render_template, flash, url_for, abort, g, current_app
from werkzeug.utils import redirect

from app.auth.routes import is_admin, get_current_user
from app.book import book_bp
from app.book.forms import NewBookForm, DeleteAllBooksForm, EditBookWarehouseCopies, RentBookForm
from db.db_service import get_db


@book_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = _setup_form(cursor)

    if form.validate_on_submit():
        # Check if book already exist
        # (NOTE: criteria - books with same title, author and publish year are the same books, with same id)
        cursor.execute("""SELECT id FROM book WHERE title=%s AND year_published=%s AND author_id=%s""",
                       (form.title.data.upper(), form.year_published.data, form.author.data))
        book_id = cursor.fetchone()

        # If not found - insert new record
        if not book_id:
            cursor.execute("""INSERT INTO book (title, year_published, author_id) VALUES (%s,%s,%s) RETURNING id;""",
                           (form.title.data.upper(), form.year_published.data, form.author.data))
            book_id = cursor.fetchone()
            cursor.execute("""INSERT INTO warehouse_book (warehouse_id, book_id, quantity) VALUES (%s,%s,%s)""",
                           (form.warehouse.data, book_id, form.quantity.data))

        # If found - no interaction with the book table, just update quantity in the warehouse
        else:
            # Check if book already have some copies in the selected warehouse
            cursor.execute("""SELECT warehouse_id, quantity FROM warehouse_book WHERE book_id=%s AND warehouse_id=%s""",
                           (book_id, form.warehouse.data))
            try:
                warehouse_id, quantity = cursor.fetchone()
                cursor.execute("""UPDATE warehouse_book SET quantity=%s WHERE warehouse_id=%s AND book_id=%s""",
                               (quantity + form.quantity.data, warehouse_id, book_id))
            # If it doesn't, insert new entry in warehouse_book
            except TypeError:
                cursor.execute("""INSERT INTO warehouse_book (warehouse_id, book_id, quantity) VALUES (%s,%s,%s)""",
                               (form.warehouse.data, book_id, form.quantity.data))
        conn.commit()
        flash(f"Book: {form.title.data.upper()} added successfully.", "success")
        return redirect(url_for("home.home"))

    return render_template("new_book.html", form=form)

def _setup_form(cursor) -> NewBookForm:
    form = NewBookForm()
    form.set_choices(cursor, "author")
    form.set_choices(cursor, "warehouse")
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
    if not is_admin(get_current_user()):
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

def get_book_data(cursor, book_id=None) -> list[tuple]:
    cursor.execute("""SELECT b.id, b.title, b.year_published, a.name, a.id, w.name, wb.quantity FROM book AS b
                      INNER JOIN author AS a ON b.author_id=a.id
                      INNER JOIN warehouse_book AS wb ON wb.book_id=b.id
                      INNER JOIN warehouse AS w ON w.id=wb.warehouse_id WHERE b.id=COALESCE(%s, b.id)""",
                   (str(book_id),) if book_id is not None else (None,))
    return cursor.fetchall()

def generate_book_dict(data: list[tuple]) -> dict:
    book_dict = {}
    for row in data:
        book_id = row[0]
        title = row[1]
        year_published = row[2]
        author = row[3]
        author_id = row[4]
        warehouse = row[5]
        quantity = row[6]
        if book_id not in book_dict:
            book_dict[book_id] = {
                'id': book_id,
                'title': title,
                'year_published': year_published,
                'author': author,
                'author_id': author_id,
                'warehouses': {}
            }
        book_dict[book_id]['warehouses'][warehouse] = quantity
    return book_dict

@book_bp.route("/delete_all/<uuid:book_id>", methods=["POST"])
def delete_all(book_id: uuid.UUID):
    if not is_admin(get_current_user()):
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

