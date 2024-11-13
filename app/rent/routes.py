import uuid
from datetime import datetime, timedelta

from flask import flash, redirect, url_for, current_app, g, render_template, session

from app.auth.routes import get_current_user, restore_from_basket
from app.rent import rent_bp
from app.rent.forms import RestoreBasketForm, CheckoutForm, ReturnBookForm
from db.db_service import get_db


@rent_bp.route("/<uuid:book_id>", methods=["GET", "POST"])
def rent(book_id: uuid.UUID):
    if not get_current_user().get('email'):
        flash("You need to be logged in.", "danger")
        return redirect(url_for("home.home"))

    conn = get_db()
    cursor = conn.cursor()
    user_email = get_current_user().get('email')
    if user_email != current_app.config["ADMIN_EMAIL"]:
        cursor.execute("""SELECT b.id, b.title, wb.warehouse_id, wb.quantity FROM book AS b
                          INNER JOIN warehouse_book AS wb ON b.id=wb.book_id
                          WHERE b.id=%s""", (str(book_id),))
        id_of_book, title, warehouse_id, quantity = cursor.fetchone()
        print(id_of_book, title, warehouse_id, quantity)
        if quantity:
            session.setdefault('member_basket', {})
            user_basket = session['member_basket'].setdefault(user_email, {})

            if str(book_id) in user_basket:
                flash("This book is already in your basket.", "danger")
            else:
                user_basket[str(book_id)] = [title, warehouse_id]
                cursor.execute("""UPDATE warehouse_book SET quantity=%s 
                                  WHERE warehouse_id=%s AND book_id=%s""", ((quantity-1), warehouse_id, id_of_book))
                conn.commit()
                flash("Book added to your rent basket.", "success")
        else:
            flash("Sorry, all copies of this book are currently rented", "danger")
    return redirect(url_for("home.home"))

@rent_bp.route("/basket")
def view_basket():
    if not get_current_user().get('email'):
        flash("You need to be logged in.", "danger")
        return redirect(url_for("home.home"))

    books_in_basket = get_basket()
    restore_basket_form = RestoreBasketForm()
    checkout_form = CheckoutForm()
    return render_template("basket.html", books=list(books_in_basket.values()), restoreBasketForm=restore_basket_form, checkoutForm=checkout_form)

@rent_bp.route("/clear", methods=["POST"])
def clear_basket():
    if not get_current_user().get('email'):
        flash("You need to be logged in.", "danger")
        return redirect(url_for("home.home"))

    restore_from_basket()
    flash("Basket cleared.", "success")
    return redirect(url_for("home.home"))

@rent_bp.route("/checkout", methods=["POST"])
def checkout():
    member_id = get_current_user().get('email')
    if not member_id:
        flash("You need to be logged in.", "danger")
        return redirect(url_for("home.home"))

    try:
        books = list(get_basket().keys())
        basket = session.get("member_basket")
        basket.pop(get_current_user().get("email"))
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO rental (borrow_date, return_date, member_id) VALUES (%s,%s,%s) RETURNING id""",
                       (datetime.now().date(), datetime.now().date()+timedelta(days=14), member_id))
        rental_id = cursor.fetchone()
        for book in books:
            cursor.execute("""INSERT INTO rental_book (rental_id, book_id) VALUES (%s,%s)""",
                           (rental_id, book))
        conn.commit()
        flash("Order made successfully.", "success")
    except (KeyError, AttributeError):
        flash("Your basket is empty.", "danger")
    return redirect(url_for("home.home"))

@rent_bp.route("/rents")
def rents():
    member_id = get_current_user().get('email')
    if not member_id:
        flash("You need to be logged in.", "danger")
        return redirect(url_for("home.home"))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT b.id, b.title, r.borrow_date, r.return_date FROM rental AS r
                          INNER JOIN rental_book AS rb ON rb.rental_id=r.id 
                          INNER JOIN book AS b ON rb.book_id=b.id
                          WHERE r.member_id=%s""", (member_id,))
    data = cursor.fetchall()
    rent_dict = {}
    for row in data:
        book_id = row[0]
        book_title = row[1]
        borrow_date = row[2]
        return_date = row[3]
        if member_id not in rent_dict:
            rent_dict[member_id] = {
                'borrow_date': borrow_date,
                'return_date': return_date,
                'books': {}
            }
        rent_dict[member_id]['books'].update({book_id: book_title})
    return render_template("rented_books.html", rents=rent_dict)

@rent_bp.route("/return", methods=["GET", "POST"])
def return_book():
    member_id = get_current_user().get('email')
    if not member_id:
        flash("You need to be logged in.", "danger")
        return redirect(url_for("home.home"))

    conn = get_db()
    cursor = conn.cursor()
    form = ReturnBookForm()
    form.set_choices(cursor, member_id)
    if form.validate_on_submit():
        cursor.execute("""SELECT r.id FROM rental AS r
                          INNER JOIN rental_book AS rb ON rb.rental_id=r.id
                          WHERE r.member_id=%s AND rb.book_id=%s""", (member_id, form.book.data))
        rent_id = cursor.fetchone()[0]
        cursor.execute("""DELETE FROM rental_book WHERE rental_id=%s AND book_id=%s""", (rent_id, form.book.data))
        cursor.execute("""SELECT warehouse_id, quantity FROM warehouse_book WHERE book_id=%s""", (form.book.data,))
        warehouse_id, quantity = cursor.fetchone()
        cursor.execute("""UPDATE warehouse_book SET quantity=%s WHERE warehouse_id=%s AND book_id=%s""",
                       (quantity+1, warehouse_id, form.book.data))
        conn.commit()
        flash("Book returned successfully.", "success")
        return redirect(url_for("home.home"))

    return render_template("return_book.html", form=form)

def get_basket() -> dict:
    basket = session.get("member_basket")
    books_in_basket = {}
    if basket:
        books_in_basket = basket[get_current_user().get("email")]
    return books_in_basket

