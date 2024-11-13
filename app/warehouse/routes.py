import uuid

from flask import render_template, flash, url_for, abort
from werkzeug.utils import redirect

from app.auth.routes import is_admin, get_current_user
from app.warehouse import warehouse_bp
from app.warehouse.forms import NewWarehouseForm, EditWarehouseForm, DeleteWarehouseForm
from db.db_service import get_db


@warehouse_bp.route("/<uuid:warehouse_id>")
def warehouse(warehouse_id: uuid.UUID):
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT w.id, w.name, w.address, b.id, b.title FROM warehouse AS w
                      LEFT JOIN warehouse_book AS wb ON w.id=wb.warehouse_id
                      LEFT JOIN book AS b ON wb.book_id=b.id
                      WHERE w.id=%s""", (str(warehouse_id),))
    warehouse_in_db = cursor.fetchall()
    warehouse_dict = {}
    if warehouse_in_db:
        for row in warehouse_in_db:
            id_of_warehouse = row[0]
            name = row[1]
            address = row[2]
            id_of_book = row[3]
            book_title = row[4]
            if id_of_warehouse not in warehouse_dict:
                warehouse_dict[id_of_warehouse] = {
                    'id': id_of_warehouse,
                    'name': name,
                    'address': address,
                    'books': []
                }
            if id_of_book is not None:
                warehouse_dict[id_of_warehouse]['books'].append({id_of_book: book_title})
        warehouse_dict = next(iter(warehouse_dict.values()))
        return render_template("warehouse.html", warehouse=warehouse_dict)
    else:
        flash("That warehouse doesnt exist.", "danger")
        return redirect(url_for("warehouse.view_all"))

@warehouse_bp.route("/")
def view_all():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""SELECT id, name, address FROM warehouse""")
    warehouses_in_db = cursor.fetchall()
    warehouses = []
    for row in warehouses_in_db:
        warehouse = {
            "id": row[0],
            "name": row[1],
            "address": row[2]
        }
        warehouses.append(warehouse)
    return render_template("warehouses.html", warehouses=warehouses)

@warehouse_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = NewWarehouseForm()
    if form.validate_on_submit():
        cursor.execute("""INSERT INTO warehouse (name, address) VALUES (%s, %s)""",
                       (form.name.data, form.address.data))
        conn.commit()
        flash(f"Warehouse {form.name.data} added successfully.", "success")
        return redirect(url_for("warehouse.view_all"))
    return render_template("new_warehouse.html", form=form)

@warehouse_bp.route("/delete", methods=["GET", "POST"])
def delete():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = DeleteWarehouseForm()
    form.set_choices(cursor)
    if form.validate_on_submit():
        cursor.execute("""DELETE FROM warehouse WHERE id=%s""", (form.warehouse.data,))
        conn.commit()
        flash("Warehouse deleted successfully.", "success")
        return redirect(url_for("warehouse.view_all"))
    return render_template("delete_warehouse.html", form=form)

@warehouse_bp.route("/edit", methods=["GET", "POST"])
def edit():
    if not is_admin(get_current_user()):
        abort(401)

    conn = get_db()
    cursor = conn.cursor()
    form = EditWarehouseForm()
    form.set_choices(cursor)
    if form.validate_on_submit():
        cursor.execute("""UPDATE warehouse SET name=%s, address=%s WHERE id=%s""",
                       (form.name.data, form.address.data, form.warehouse.data))
        conn.commit()
        flash("Warehouse updated successfully.", "success")
        return redirect(url_for("warehouse.view_all"))
    return render_template("edit_warehouse.html", form=form)