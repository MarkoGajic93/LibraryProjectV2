import logging
import uuid

from flask import render_template, flash, url_for, abort
from werkzeug.utils import redirect

from app import db
from app.auth.routes import is_admin
from app.db_models import Warehouse
from app.warehouse import warehouse_bp
from app.warehouse.forms import NewWarehouseForm, EditWarehouseForm, DeleteWarehouseForm


@warehouse_bp.route("/<uuid:warehouse_id>")
def warehouse(warehouse_id: uuid.UUID):
    if not is_admin():
        logging.warning(f"Unauthorized attempt to access warehouse {warehouse_id}.")
        abort(401)

    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        flash("That warehouse doesnt exist.", "danger")
        logging.warning(f"Attempt to access non-existent warehouse {warehouse_id}.")
        return redirect(url_for("warehouse.view_all"))
    return render_template("warehouse.html", warehouse=warehouse)

@warehouse_bp.route("/")
def view_all():
    if not is_admin():
        logging.warning(f"Unauthorized attempt to access warehouses.")
        abort(401)

    warehouses = Warehouse.query.all()
    return render_template("warehouses.html", warehouses=warehouses)

@warehouse_bp.route("/new", methods=["GET", "POST"])
def add_new():
    if not is_admin():
        logging.warning(f"Unauthorized attempt to create new warehouse.")
        abort(401)

    form = NewWarehouseForm()
    if form.validate_on_submit():
        warehouse = Warehouse(form.name.data, form.address.data)
        db.session.add(warehouse)
        try:
            db.session.commit()
            flash(f"Warehouse {form.name.data} added successfully.", "success")
            logging.info(f"Warehouse {form.name.data} added successfully.")
            return redirect(url_for("warehouse.view_all"))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating new warehouse: {e}.", "danger")
            logging.warning(f"An error occurred while creating new warehouse: {e}.")
    return render_template("new_warehouse.html", form=form)

@warehouse_bp.route("/delete", methods=["GET", "POST"])
def delete():
    if not is_admin():
        logging.warning(f"Unauthorized attempt to delete warehouse.")
        abort(401)

    form = DeleteWarehouseForm()
    form.set_choices()
    form.set_choices()
    if form.validate_on_submit():
        warehouse = Warehouse.query.get(form.warehouse.data)
        if not warehouse:
            flash("Warehouse doesn't exist.", "danger")
            logging.warning(f"Attempt to delete non-existent warehouse.")
            return redirect(url_for("warehouse.view_all"))

        db.session.delete(warehouse)
        try:
            db.session.commit()
            flash("Warehouse deleted successfully.", "success")
            logging.info(f"Warehouse deleted successfully.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while deleting warehouse: {e}.", "danger")
            logging.warning(f"An error occurred while deleting warehouse: {e}.")
        return redirect(url_for("warehouse.view_all"))
    return render_template("delete_warehouse.html", form=form)

@warehouse_bp.route("/edit", methods=["GET", "POST"])
def edit():
    if not is_admin():
        logging.warning(f"Unauthorized attempt to update warehouse.")
        abort(401)

    form = EditWarehouseForm()
    form.set_choices()
    if form.validate_on_submit():
        warehouse = Warehouse.query.get(form.warehouse.data)
        if not warehouse:
            flash("Warehouse doesn't exist.", "danger")
            logging.warning(f"Attempt to update non-existent warehouse.")
            return redirect(url_for("warehouse.view_all"))

        warehouse.name = form.name.data
        warehouse.address = form.address.data
        db.session.add(warehouse)
        try:
            db.session.commit()
            flash("Warehouse updated successfully.", "success")
            logging.info(f"Warehouse updated successfully.")
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating warehouse: {e}.", "danger")
            logging.warning(f"An error occurred while updating warehouse: {e}.")
        return redirect(url_for("warehouse.view_all"))
    return render_template("edit_warehouse.html", form=form)