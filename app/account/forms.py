from enum import member

from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, EmailField, SubmitField, PasswordField
from wtforms.validators import InputRequired, DataRequired, ValidationError

from app.db_models import Member


class EditAccountForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired("Input is required!"), DataRequired("Data is required!")])
    email = EmailField("Email",
                       validators=[InputRequired("Input is required!"),
                                   DataRequired("Data is required!")])
    age = SelectField("Age", choices=[(str(age), str(age)) for age in range(1, 99)])
    phone = StringField("Phone number")
    submit = SubmitField("Submit")

    def validate_email(form, field):
        member = Member.query.filter_by(email=field.data).first()
        if member:
            raise ValidationError("Email already exists.")

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password")
    new_password = PasswordField("New password")
    submit = SubmitField("Submit")