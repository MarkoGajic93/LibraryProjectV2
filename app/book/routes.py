import logging
import uuid

from flask import render_template, flash, url_for, abort
from werkzeug.utils import redirect

from app import db
from app.auth.routes import is_admin
from app.book import book_bp
from app.book.forms import NewBookForm, DeleteAllBooksForm, EditBookWarehouseCopies, RentBookForm
from app.db_models import Book, WarehouseBook, Warehouse


@book_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin():
        logging.warning(f"Unauthorized attempt to create new book.")
        abort(401)

    form = _setup_form()

    if form.validate_on_submit():
        # Check if book already exist
        # (NOTE: criteria - books with same title, author and publish year are the same books, with same id)
        book = (Book.query.filter_by(title=form.title.data, year_published=form.year_published.data, author_id=form.author.data).first())

        # If not found - insert new record
        if not book:
            book = Book(title=form.title.data.upper(), year_published=form.year_published.data, author_id=form.author.data)
            db.session.add(book)
            db.session.flush()
            warehouse_book = WarehouseBook(form.warehouse.data, book.id, form.quantity.data)
            db.session.add(warehouse_book)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while creating book: {e}.", "danger")
                logging.warning(f"An error occurred while creating book: {e}.")

        # If found - no interaction with the book table, just update quantity in the warehouse
        else:
            warehouse_book = WarehouseBook.query.filter_by(warehouse_id=form.warehouse.data, book_id=book.id).first()
            # Check if book already have some copies in the selected warehouse
            if warehouse_book:
                warehouse_book.quantity = warehouse_book.quantity+form.quantity.data
            # If it doesn't, create new warehouse_book
            else:
                warehouse_book = WarehouseBook(form.warehouse.data, book.id, form.quantity.data)
            db.session.add(warehouse_book)
        try:
            db.session.commit()
            flash(f"Book: {form.title.data.upper()} added successfully.", "success")
            logging.info(f"Book: {form.title.data.upper()} added successfully.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating new book: {e}.", "danger")
            logging.warning(f"An error occurred while creating book: {e}.")
        return redirect(url_for("home.home"))

    return render_template("new_book.html", form=form)

def _setup_form() -> NewBookForm:
    form = NewBookForm()
    form.set_choices("Author")
    form.set_choices("Warehouse")
    return form

@book_bp.route("/<uuid:book_id>")
def book(book_id: uuid.UUID):

    delete_all_books_form = DeleteAllBooksForm()
    rent_book_form = RentBookForm()
    book = Book.query.get(book_id)
    if book:
        return render_template("book.html",
                               book=book,
                               deleteAllBooksForm=delete_all_books_form,
                               rentBookForm=rent_book_form)
    else:
        flash("That book doesnt exist", "danger")
        logging.warning(f"Attempt to access non-existent book.")
        return redirect(url_for("home.home"))

@book_bp.route("/edit/<uuid:book_id>", methods=["GET", "POST"])
def manage_copies(book_id: uuid.UUID):
    if not is_admin():
        logging.warning(f"Unauthorized attempt to edit book copies.")
        abort(401)

    book = Book.query.get(book_id)
    if not book:
        flash("That book doesn't exist.", "danger")
        logging.warning(f"Attempt to manage copies of non-existent book.")
        return redirect(url_for("home.home"))

    edit_form = EditBookWarehouseCopies()
    edit_form.warehouse.choices = [(warehouse.id, warehouse.name) for warehouse in Warehouse.query.all()]

    if edit_form.validate_on_submit():
        warehouse_book = WarehouseBook.query.filter_by(warehouse_id=edit_form.warehouse.data, book_id=book_id).first()

        if edit_form.quantity.data == 0:
            if warehouse_book:
                db.session.delete(warehouse_book)
            if not book.warehouses:
                db.session.delete(book)
        else:
            if warehouse_book:
                warehouse_book.quantity = edit_form.quantity.data
            else:
                new_warehouse_book = WarehouseBook(edit_form.warehouse.data, book_id, edit_form.quantity.data)
                db.session.add(new_warehouse_book)
        try:
            db.session.commit()
            flash(f"Book {book.title} updated successfully.", "success")
            logging.info(f"Book {book.title} updated successfully.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating the book: {e}.", "danger")
            logging.warning(f"An error occurred while updating the book: {e}.")

        return redirect(url_for('book.book', book_id=book_id))
    return render_template("edit_copies.html", book=book, editForm=edit_form)

@book_bp.route("/delete_all/<uuid:book_id>", methods=["POST"])
def delete_all(book_id: uuid.UUID):
    if not is_admin():
        logging.warning(f"Unauthorized attempt to delete book copies.")
        abort(401)

    book = Book.query.filter_by(id=book_id).first()
    if not book:
        flash(f"Book doesnt exist.", "danger")
        return redirect(url_for("home.home"))

    db.session.delete(book)
    try:
        db.session.commit()
        flash(f"Book {book.title} deleted successfully from all warehouses.", "success")
        logging.info(f"Book {book.title} deleted successfully from all warehouses.")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting the book: {e}.", "danger")
        logging.warning(f"An error occurred while deleting the book: {e}.")
    return redirect(url_for("home.home"))

