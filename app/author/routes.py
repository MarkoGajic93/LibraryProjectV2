import uuid

from flask import render_template, flash, url_for, abort
from werkzeug.utils import redirect

from app import db
from app.auth.routes import is_admin, get_current_user
from app.author import author_bp
from app.author.forms import NewAuthorForm, DeleteAuthorForm, EditAuthorForm
from app.db_models import Author
from db.db_service import get_db


@author_bp.route("/<uuid:author_id>")
def author(author_id: uuid.UUID):
    author = Author.query.filter_by(id=author_id).first()
    if not author:
        flash("That author doesnt exist.", "danger")
        return redirect(url_for("author.view_all"))
    return render_template("author.html", author=author)

@author_bp.route("/")
def view_all():
    authors = Author.query.all()
    return render_template("authors.html", authors=authors)

@author_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin():
        abort(401)

    form = NewAuthorForm()
    if form.validate_on_submit():
        author = Author(form.name.data, form.biography.data)
        db.session.add(author)
        try:
            db.session.commit()
            flash(f"Author {form.name.data} added successfully.", "success")
            return redirect(url_for("author.view_all"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating new author: {e}.", "danger")
    return render_template("new_author.html", form=form)

@author_bp.route("/delete", methods=["GET", "POST"])
def delete():
    if not is_admin():
        abort(401)

    form = DeleteAuthorForm()
    form.set_choices()
    if form.validate_on_submit():
        author = Author.query.filter_by(id=form.author.data).first()
        if not author:
            flash("Author doesn't exist.", "danger")
            return redirect(url_for("author.view_all"))

        db.session.delete(author)
        try:
            db.session.commit()
            flash("Author deleted successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while deleting author: {e}.", "danger")
        return redirect(url_for("author.view_all"))
    return render_template("delete_author.html", form=form)

@author_bp.route("/edit", methods=["GET", "POST"])
def edit():
    if not is_admin():
        abort(401)

    form = EditAuthorForm()
    form.set_choices()
    if form.validate_on_submit():
        author = Author.query.filter_by(id=form.author.data).first()
        if not author:
            flash("Author doesn't exist.", "danger")
            return redirect(url_for("author.view_all"))

        author.name = form.name.data
        author.biography = form.biography.data
        db.session.add(author)
        try:
            db.session.commit()
            flash("Author updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating author: {e}.", "danger")
        return redirect(url_for("author.view_all"))
    return render_template("edit_author.html", form=form)