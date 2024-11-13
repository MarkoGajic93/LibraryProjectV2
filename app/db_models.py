import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app import db

class Member(db.Model):
    __tablename__ = "member"

    email = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(255))

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

class WarehouseBook(db.Model):
    __tablename__ = "warehouse_book"
    warehouse_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("warehouse.id", ondelete="CASCADE"), primary_key=True)
    book_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey("book.id", ondelete="CASCADE"), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    book = db.relationship("Book", back_populates="warehouses")
    warehouse = db.relationship("Warehouse", back_populates="books")

