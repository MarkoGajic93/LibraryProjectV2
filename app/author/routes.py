import uuid

from flask import render_template, flash, url_for, abort
from werkzeug.utils import redirect

from app.auth.routes import is_admin, get_current_user
from app.author import author_bp
from app.author.forms import NewAuthorForm, DeleteAuthorForm, EditAuthorForm
from db.db_service import get_db


@author_bp.route("/<uuid:author_id>")
def author(author_id: uuid.UUID):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT a.id, a.name, a.biography, b.id, b.title FROM author AS a
                      LEFT JOIN book AS b ON a.id=b.author_id
                      WHERE a.id=%s""", (str(author_id),))
    author_in_db = cursor.fetchall()
    author_dict = {}
    if author_in_db:
        for row in author_in_db:
            id_of_author = row[0]
            name = row[1]
            biography = row[2]
            id_of_book = row[3]
            book_title = row[4]
            if id_of_author not in author_dict:
                author_dict[id_of_author] = {
                    'id': id_of_author,
                    'name': name,
                    'biography': biography,
                    'books': []
                }
            if id_of_book is not None:
                author_dict[id_of_author]['books'].append({id_of_book: book_title})
        author_dict = next(iter(author_dict.values()))
        return render_template("author.html", author=author_dict)
    else:
        flash("That author doesnt exist.", "danger")
        return redirect(url_for("author.view_all"))

@author_bp.route("/")
def view_all():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, name, biography FROM author""")
    authors_in_db = cursor.fetchall()
    authors = []
    for row in authors_in_db:
        author = {
            "id": row[0],
            "name": row[1],
            "biography": row[2]
        }
        authors.append(author)
    return render_template("authors.html", authors=authors)

@author_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = NewAuthorForm()
    if form.validate_on_submit():
        cursor.execute("""INSERT INTO author (name, biography) VALUES (%s, %s)""",
                       (form.name.data, form.biography.data))
        conn.commit()
        flash(f"Author {form.name.data} added successfully.", "success")
        return redirect(url_for("author.view_all"))
    return render_template("new_author.html", form=form)

@author_bp.route("/delete", methods=["GET", "POST"])
def delete():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = DeleteAuthorForm()
    form.set_choices(cursor)
    if form.validate_on_submit():
        cursor.execute("""DELETE FROM author WHERE id=%s""", (form.author.data,))
        conn.commit()
        flash("Author deleted successfully.", "success")
        return redirect(url_for("author.view_all"))
    return render_template("delete_author.html", form=form)

@author_bp.route("/edit", methods=["GET", "POST"])
def edit():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = EditAuthorForm()
    form.set_choices(cursor)
    if form.validate_on_submit():
        cursor.execute("""UPDATE author SET name=%s, biography=%s WHERE id=%s""",
                       (form.name.data, form.biography.data, form.author.data))
        conn.commit()
        flash("Author updated successfully.", "success")
        return redirect(url_for("author.view_all"))
    return render_template("edit_author.html", form=form)