import logging

from flask import abort, render_template, url_for, flash, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from . import account_bp
from .forms import EditAccountForm, ChangePasswordForm
from .. import db
from ..auth.routes import is_admin, get_current_user
from ..db_models import Member


@account_bp.route("/<string:member_id>")
def member(member_id: str):
    if not (is_admin() or get_current_user().email == member_id):
        logging.warning("Unauthorized attempt to view member data.")
        abort(401)
    user = Member.query.get(member_id)
    return render_template("account.html", user=user)

@account_bp.route("/delete/<string:member_id>", methods=["POST"])
def delete(member_id: str):
    if not (is_admin() or get_current_user().email == member_id):
        logging.warning("Unauthorized attempt to delete member account.")
        abort(401)

    if request.method == "POST":
        user = Member.query.get(member_id)
        if user.rents:
            flash(f"Cannot delete account until all rented books are returned.", "danger")
            logging.warning(f"Failed attempt to delete account (user have books rented).")
            return redirect(url_for("rent.rents"))
        db.session.delete(user)
        try:
            db.session.commit()
            session.pop("user")
            flash(f"Account deleted successfully.", "success")
            logging.info(f"Account deleted successfully.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while deleting account: {e}.", "danger")
            logging.warning(f"An error occurred while deleting account: {e}.")
    return redirect(url_for("home.home"))

@account_bp.route("/edit/<string:member_id>", methods=["GET","POST"])
def edit(member_id: str):
    if get_current_user().email != member_id:
        logging.warning("Unauthorized attempt to edit member account.")
        abort(401)

    user = Member.query.get(member_id)
    form = EditAccountForm()
    if request.method == 'GET':
        form.name.data = user.name
        form.email.data = user.email
        form.age.data = str(user.age)
        form.phone.data = user.phone_number

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.age = form.age.data
        user.phone_number = form.phone.data
        db.session.add(user)
        try:
            db.session.commit()
            user_basket = session["user"].setdefault('member_basket', {})
            session["user"] = {"email": user.email, "name": user.name, "member_basket": user_basket}
            flash(f"Account updated successfully.", "success")
            logging.warning(f"Account updated successfully.")
            return render_template("account.html", user=user)
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating account: {e}.", "danger")
            logging.warning(f"An error occurred while updating account: {e}.")
    return render_template("edit_account.html", form=form, member_id=member_id)

@account_bp.route("/password/<string:member_id>", methods=["GET", "POST"])
def change_password(member_id: str):
    form = ChangePasswordForm()
    user = Member.query.get(member_id)
    if form.validate_on_submit():
        if check_password_hash(user.password, form.old_password.data):
            user.password = generate_password_hash(form.new_password.data)
            db.session.add(user)
            try:
                db.session.commit()
                flash(f"Password changed successfully.", "success")
                logging.warning(f"Password changed successfully for {user.email}.")
                return render_template("account.html", user=user)
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while updating account: {e}.", "danger")
                logging.warning(f"An error occurred while updating account: {e}.")
        flash("Incorrect old password", "danger")
        logging.warning(f"Failed change password attempt for user: {user.email} (wrong old password).")
    return render_template("change_password.html", form=form, member_id=member_id)