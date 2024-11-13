import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

from app import db

class Member(db.Model):
    __tablename__ = "member"

    email = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(255))

    def __init__(self, name="", email="", password="", age="", phone_number=""):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.age = age
        self.phone_number = phone_number

class Author(db.Model):
    __tablename__ = "author"
    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    biography = db.Column(db.Text)

    books = db.relationship("Book", back_populates="author")

class Warehouse(db.Model):
    __tablename__ = "warehouse"
    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)

    books = db.relationship("WarehouseBook", back_populates="warehouse")

class Book(db.Model):
    __tablename__ = "book"

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    author_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("author.id", ondelete="CASCADE"), nullable=False)

    author = db.relationship("Author", back_populates="books")
    warehouses = db.relationship("WarehouseBook", back_populates="book")

    def __init__(self, title, year_published, author_id):
        self.title = title
        self.year_published = year_published
        self.author_id = author_id

class WarehouseBook(db.Model):
    __tablename__ = "warehouse_book"
    warehouse_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("warehouse.id", ondelete="CASCADE"), primary_key=True)
    book_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    book = db.relationship("Book", back_populates="warehouses")
    warehouse = db.relationship("Warehouse", back_populates="books")

    def __init__(self, warehouse_id, book_id, quantity):
        self.warehouse_id = warehouse_id
        self.book_id = book_id
        self.quantity = quantity

