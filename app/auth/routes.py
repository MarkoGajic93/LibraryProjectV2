import logging

from flask import render_template, flash, url_for, session, g, current_app
from werkzeug.security import check_password_hash
from werkzeug.utils import redirect

from app import db
from app.auth import auth_bp
from app.auth.forms import MemberRegisterForm, MemberLoginForm
from app.db_models import Member, WarehouseBook


@auth_bp.app_context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user().email:
        flash("You are already registered.", "danger")
        logging.warning(f"Logged in user tried to register.")
        return redirect(url_for("home.home"))

    form = MemberRegisterForm()
    if form.validate_on_submit():
        member = Member(form.name.data, form.email.data, form.password.data, form.age.data, form.phone.data)
        db.session.add(member)
        try:
            db.session.commit()
            flash(f"{form.name.data} successfully registered.", "success")
            logging.info(f"{form.name.data} successfully registered.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating new member: {e}.", "danger")
            logging.warning(f"An error occurred while creating new member: {e}.")

        return redirect(url_for('home.home'))
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user().email:
        flash("You are already logged in.", "danger")
        logging.warning(f"Logged in user tried to login.")
        return redirect(url_for("home.home"))

    form = MemberLoginForm()
    if form.validate_on_submit():
        member = Member.query.filter_by(email=form.email.data).first()
        if not member:
            flash(f"Member with email: {form.email.data} doesnt exist", "danger")
            logging.warning(f"Failed login attempt with non-existent email: {form.email.data}.")
            return render_template("login.html", form=form)
        if check_password_hash(member.password, form.password.data):
            session["user"] = {'email': form.email.data, 'name': member.name}
            flash(f"{member.name} logged in successfully", "success")
            logging.info(f"{member.name} logged in successfully.")
            return redirect(url_for("home.home"))
        flash("Incorrect password", "danger")
        logging.warning(f"Failed login attempt with email: {form.email.data} (wrong password).")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
def logout():
    try:
        if session.get("member_basket"):
            restore_from_basket()
            session.pop("member_basket")
        user = session.pop("user")
        flash(f"{user['name']} logged out.", "success")
        logging.info(f"{user['name']} logged out successfully.")
    except KeyError:
        flash("You are not logged in.", "danger")
        logging.warning(f"Failed attempt to logout (user was not logged in).")
    return redirect(url_for("home.home"))

def get_current_user() -> Member:
    _current_user = getattr(g, "_current_user", None)
    if not _current_user:
        if session.get("user"):
            _current_user = g._current_user = Member.query.filter_by(email=session['user']['email']).first()
        else:
            _current_user = Member()
    return _current_user

def is_admin() -> bool:
    return get_current_user().email == current_app.config["ADMIN_EMAIL"]

def restore_from_basket():
    basket = session.get("member_basket")
    if not basket:
        return

    books_in_basket = basket[get_current_user().email]
    for book_id in books_in_basket.keys():
        warehouse_id = books_in_basket[book_id][1]
        warehouse_book = WarehouseBook.query.filter_by(warehouse_id=warehouse_id, book_id=book_id).first()
        warehouse_book.quantity += 1
    try:
        db.session.commit()
        session.pop("member_basket")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while restoring from basket: {e}.", "danger")
        logging.warning(f"An error occurred while restoring from basket: {e}.")
