from flask_wtf import FlaskForm
from sqlalchemy.orm import joinedload
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField

from app.db_models import Rental, Book


class CheckoutForm(FlaskForm):
    submit = SubmitField("Checkout")

class RestoreBasketForm(FlaskForm):
    submit = SubmitField("Clear basket")

class ReturnBookForm(FlaskForm):
    book = SelectField("Book")
    submit = SubmitField("Return")

    def set_choices(self, member_id):
        rentals = Rental.query.options(joinedload(Rental.books)).filter_by(member_id=member_id).all()
        book_ids = [book.book_id for rental in rentals for book in rental.books]
        book_titles = [Book.query.get(book_id).title for book_id in book_ids]
        options = list(zip(book_ids, book_titles))
        self.book.choices = options