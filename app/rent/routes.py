import logging
import uuid
from datetime import datetime, timedelta

from flask import flash, redirect, url_for, current_app, render_template, session
from sqlalchemy.orm import joinedload

from app import db
from app.auth.routes import get_current_user, restore_from_basket
from app.db_models import Book, WarehouseBook, Rental, RentalBook
from app.rent import rent_bp
from app.rent.forms import RestoreBasketForm, CheckoutForm, ReturnBookForm


@rent_bp.route("/<uuid:book_id>", methods=["GET", "POST"])
def rent(book_id: uuid.UUID):
    user = get_current_user()
    if not user.email:
        flash("You need to be logged in.", "danger")
        logging.warning(f"Failed attempt to rent a book (user is not logged in).")
        return redirect(url_for("home.home"))

    if user.email != current_app.config["ADMIN_EMAIL"]:
        book = Book.query.get(book_id)
        if not book:
            flash("That book doesnt exist", "danger")
            logging.warning(f"Attempt to rent non-existent book.")
            return redirect(url_for("home.home"))
        if book.warehouses:
            user_basket = session["user"].setdefault('member_basket', {})
            if str(book_id) in user_basket:
                flash("This book is already in your basket.", "danger")
                logging.warning(f"Attempt to rent a book that is already in user basket.")
            else:
                user_basket[str(book_id)] = [book.title, book.warehouses[0].warehouse_id]
                warehouse_book = WarehouseBook.query.filter_by(warehouse_id=book.warehouses[0].warehouse_id, book_id=book.id).first()
                warehouse_book.quantity -= 1
                db.session.add(warehouse_book)
                try:
                    db.session.commit()
                    flash("Book added to your rent basket.", "success")
                    logging.info(f"Book added to user basket successfully.")
                except Exception as e:
                    db.session.rollback()
                    flash(f"An error occurred while adding book to basket: {e}.", "danger")
                    logging.warning(f"An error occurred while adding book to basket: {e}.")
        else:
            flash("Sorry, all copies of this book are currently rented", "danger")
            logging.warning(f"Attempt to rent a book with no available copies.")
    return redirect(url_for("home.home"))

@rent_bp.route("/basket")
def view_basket():
    user = get_current_user()
    if not user.email:
        flash("You need to be logged in.", "danger")
        logging.warning(f"Failed attempt to view basket (user is not logged in).")
        return redirect(url_for("home.home"))

    books_in_basket = []
    basket = session["user"].get("member_basket", {})
    if basket:
        books_in_basket = list(basket.values())
    restore_basket_form = RestoreBasketForm()
    checkout_form = CheckoutForm()
    return render_template("basket.html", books=books_in_basket, restoreBasketForm=restore_basket_form, checkoutForm=checkout_form)

@rent_bp.route("/clear", methods=["POST"])
def clear_basket():
    user = get_current_user()
    if not user.email:
        flash("You need to be logged in.", "danger")
        logging.warning(f"Failed attempt to clear basket (user is not logged in).")
        return redirect(url_for("home.home"))

    restore_from_basket()
    flash("Basket cleared.", "success")
    logging.info(f"User cleared basket successfully.")
    return redirect(url_for("home.home"))

@rent_bp.route("/checkout", methods=["POST"])
def checkout():
    member_id = get_current_user().email
    if not member_id:
        flash("You need to be logged in.", "danger")
        logging.warning(f"Failed attempt to make rent order (user is not logged in).")
        return redirect(url_for("home.home"))

    books = []
    basket = session["user"].get("member_basket", {})
    if basket:
        books = list(basket.keys())
    if not books:
        flash(f"Your basket is empty.", "danger")
        logging.warning(f"Failed attempt to make rent order (user basket is empty).")
        return redirect(url_for("home.home"))

    rental = Rental(datetime.now().date(), datetime.now().date()+timedelta(days=14), member_id)
    db.session.add(rental)
    db.session.flush()
    for book_id in books:
        rental_book = RentalBook(rental_id=rental.id, book_id=book_id)
        db.session.add(rental_book)
    try:
        db.session.commit()
        session["user"].pop("member_basket")
        flash("Order made successfully.", "success")
        logging.info(f"User rent order created successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while making order: {e}.", "danger")
        logging.warning(f"An error occurred while making order: {e}.")

    return redirect(url_for("home.home"))

@rent_bp.route("/rents")
def rents():
    member_id = get_current_user().email
    if not member_id:
        flash("You need to be logged in.", "danger")
        logging.warning(f"Failed attempt to view rented books (user is not logged in).")
        return redirect(url_for("home.home"))

    rents = Rental.query.options(joinedload(Rental.books)).filter_by(member_id=member_id).all()
    return render_template("rented_books.html", rents=rents)

@rent_bp.route("/return", methods=["GET", "POST"])
def return_book():
    member_id = get_current_user().email
    if not member_id:
        flash("You need to be logged in.", "danger")
        logging.warning(f"Failed attempt to return a book (user is not logged in).")
        return redirect(url_for("home.home"))

    form = ReturnBookForm()
    rentals = Rental.query.options(joinedload(Rental.books)).filter_by(member_id=member_id).all()
    book_ids = [book.book_id for rental in rentals for book in rental.books]
    book_titles = [Book.query.get(book_id).title for book_id in book_ids]
    form.book.choices = list(zip(book_ids, book_titles))
    if form.validate_on_submit():
        for rental in rentals:
            for book in rental.books:
                if str(book.book_id) == form.book.data:
                    rental_id = rental.id

        rental_book = RentalBook.query.filter_by(rental_id=rental_id, book_id=form.book.data).first()
        db.session.delete(rental_book)
        rental = Rental.query.options(joinedload(Rental.books)).get(rental_id)
        warehouse_book = WarehouseBook.query.filter_by(book_id=form.book.data).first()
        warehouse_book.quantity += 1
        db.session.add(warehouse_book)
        try:
            db.session.commit()
            if not rental.books:
                db.session.delete(rental)
                db.session.commit()
            flash("Book returned successfully.", "success")
            logging.info(f"Book returned successfully.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while returning a book: {e}.", "danger")
            logging.info(f"An error occurred while returning a book: {e}.")

        return redirect(url_for("home.home"))

    return render_template("return_book.html", form=form)
