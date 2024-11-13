from flask import render_template, flash, url_for, session, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from app.auth import auth_bp
from app.auth.forms import MemberRegisterForm, MemberLoginForm
from db.db_service import get_db


@auth_bp.app_context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if get_current_user().get('email'):
        flash("You are already registered.", "danger")
        return redirect(url_for("home.home"))

    form = MemberRegisterForm()
    if form.validate_on_submit():
        conn = get_db()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(form.password.data)
        cursor.execute("INSERT INTO member (email, name, password, age, phone_number) VALUES (%s,%s,%s,%s,%s)",
                       (form.email.data, form.name.data, hashed_password, form.age.data, form.phone.data))
        conn.commit()
        flash(f"{form.name.data} successfully registered.", "success")
        return redirect(url_for('home.home'))
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if get_current_user().get('email'):
        flash("You are already logged in.", "danger")
        return redirect(url_for("home.home"))

    conn = get_db()
    cursor = conn.cursor()
    form = MemberLoginForm()
    if form.validate_on_submit():
        cursor.execute("""SELECT email, name, password FROM member WHERE email=%s""", (form.email.data,))
        email, name, hash_password = cursor.fetchone()
        if check_password_hash(hash_password, form.password.data):
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

def get_current_user() -> dict:
    _current_user = getattr(g, "_current_user", None)
    if not _current_user:
        if session.get("user"):
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""SELECT email, name, age, phone_number FROM member WHERE email=%s""", (session['user']['email'],))
            email, name, age, phone = cursor.fetchone()
            _current_user = g._current_user = {"email": email, "name": name, "age": age, "phone": phone}
        else:
            _current_user = {}
    return _current_user

def is_admin(current_user) -> bool:
    return get_current_user().get("email") == current_app.config["ADMIN_EMAIL"]

def restore_from_basket():
    basket = session.get("member_basket")
    if not basket:
        return
    conn = get_db()
    cursor = conn.cursor()
    books_in_basket = basket[get_current_user().get("email")]
    for book_id in books_in_basket.keys():
        warehouse_id = books_in_basket[book_id][1]
        cursor.execute("""SELECT quantity FROM warehouse_book WHERE book_id=%s AND warehouse_id=%s""", (book_id, warehouse_id))
        quantity = cursor.fetchone()[0]
        cursor.execute("""UPDATE warehouse_book SET quantity=%s 
                          WHERE warehouse_id=%s AND book_id=%s""",
                       ((quantity + 1), warehouse_id, book_id))
    conn.commit()
    session.pop("member_basket")