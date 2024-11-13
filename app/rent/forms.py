from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField


class CheckoutForm(FlaskForm):
    submit = SubmitField("Checkout")

class RestoreBasketForm(FlaskForm):
    submit = SubmitField("Clear basket")

class ReturnBookForm(FlaskForm):
    book = SelectField("Book")
    submit = SubmitField("Return")

    def set_choices(self, cursor, member_id):
        cursor.execute("""SELECT rb.book_id, b.title FROM rental AS r
                          INNER JOIN rental_book AS rb ON r.id=rb.rental_id
                          INNER JOIN book AS b ON rb.book_id=b.id
                          WHERE r.member_id=%s""", (member_id,))
        options = cursor.fetchall()
        self.book.choices = options