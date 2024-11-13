from typing import Literal

from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import InputRequired, DataRequired, NumberRange


class NewBookForm(FlaskForm):
    title = StringField("Title",
                        validators=[InputRequired("Input is required!"),
                                    DataRequired("Data is required!")])

    year_published = SelectField("Year published",
                                 choices=[(str(year), str(year)) for year in range(1900, 2024)],
                                 validators=[InputRequired("Input is required!")])

    author = SelectField("Author")

    warehouse = SelectField("Warehouse")

    quantity = IntegerField("Quantity",
                            validators=[InputRequired("Input is required!"),
                                        DataRequired("Data is required!"),
                                        NumberRange(min=1, message="Quantity must be a positive integer.")])

    submit = SubmitField("Add book")

    def set_choices(self, cursor, field: Literal["author", "warehouse"]):
        cursor.execute(f"SELECT id, name FROM {field}")
        options = cursor.fetchall()
        if field == "author":
            self.author.choices = options
        if field == "warehouse":
            self.warehouse.choices = options

class DeleteAllBooksForm(FlaskForm):
    submit = SubmitField("Delete all")

class RentBookForm(FlaskForm):
    submit = SubmitField("Add to basket")

class EditBookWarehouseCopies(FlaskForm):
    warehouse = SelectField("Warehouse")
    quantity = IntegerField("Quantity",
                            validators=[InputRequired("Input is required!"),
                                        NumberRange(min=0, message="Quantity must be a non-negative integer.")])
    submit = SubmitField("Submit")