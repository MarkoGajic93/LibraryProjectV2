import os

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy

import config

app_env = os.environ.get("FLASK_ENV")
db = SQLAlchemy()

def inject_config():
    return dict(config=current_app.config)

def create_app(config_env = app_env):
    app = Flask(__name__)
    app.config.from_object(f"config.{config_env.capitalize()}Config")
    app.context_processor(inject_config)
    db.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.home import home_bp
    app.register_blueprint(home_bp, url_prefix="/")

    from app.book import book_bp
    app.register_blueprint(book_bp, url_prefix="/books")

    from app.author import author_bp
    app.register_blueprint(author_bp, url_prefix="/authors")

    from app.warehouse import warehouse_bp
    app.register_blueprint(warehouse_bp, url_prefix="/warehouses")

    from app.rent import rent_bp
    app.register_blueprint(rent_bp, url_prefix="/rents")

    from app.account import account_bp
    app.register_blueprint(account_bp, url_prefix="/accounts")

    return app