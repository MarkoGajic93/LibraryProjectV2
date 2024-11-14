import logging

from flask import abort, render_template

from . import account_bp
from ..auth.routes import is_admin, get_current_user


@account_bp.route("/<string:member_id>")
def member(member_id: str):
    if not (is_admin() or get_current_user().email == member_id):
        logging.warning("Unauthorized attempt to view member data.")
        abort(401)

    return render_template("account.html")
