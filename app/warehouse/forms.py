from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Length

from app.db_models import Warehouse


class NewWarehouseForm(FlaskForm):
    name = StringField("Name",
                        validators=[InputRequired("Input is required!"),
                                    DataRequired("Data is required!")])

    address = StringField("Address",
                        validators=[InputRequired("Input is required!"),
                                    DataRequired("Data is required!")])

    submit = SubmitField("Add warehouse")

class DeleteWarehouseForm(FlaskForm):
    warehouse = SelectField("Warehouse")
    submit = SubmitField("Submit")

    def set_choices(self):
        self.warehouse.choices = [(warehouse.id, warehouse.name) for warehouse in Warehouse.query.all()]

class EditWarehouseForm(DeleteWarehouseForm):
    name = StringField("Edit name",
                       validators=[InputRequired("Input is required!"),
                                   DataRequired("Data is required!")])
    address = StringField("Edit address",
                          validators=[InputRequired("Input is required!"),
                                      DataRequired("Data is required!")])