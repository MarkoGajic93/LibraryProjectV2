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
        return redirect(url_for("home.home"))

    form = MemberRegisterForm()
    if form.validate_on_submit():
        member = Member(form.name.data, form.email.data, form.password.data, form.age.data, form.phone.data)
        db.session.add(member)
        try:
            db.session.commit()
            flash(f"{form.name.data} successfully registered.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating new member: {e}.", "danger")

        return redirect(url_for('home.home'))
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user().email:
        flash("You are already logged in.", "danger")
        return redirect(url_for("home.home"))

    form = MemberLoginForm()
    if form.validate_on_submit():
        name, email, password = Member.query.with_entities(Member.name, Member.email, Member.password).filter_by(email=form.email.data).first()
        if not email:
            flash(f"Member with email: {form.email.data} doesnt exist", "danger")
        if check_password_hash(password, form.password.data):
            session["user"] = {'email': email, 'name': name}
            flash(f"{name} logged in successfully", "success")
            return redirect(url_for("home.home"))
        flash("Incorrect password", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/logout")
def logout():
    try:
        if session.get("member_basket"):
            restore_from_basket()
            session.pop("member_basket")
        user = session.pop("user")
        flash(f"{user['name']} logged out.", "success")
    except KeyError:
        flash("You are not logged in.", "danger")
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
