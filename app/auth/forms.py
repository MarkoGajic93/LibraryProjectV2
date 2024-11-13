from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import EmailField, StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, DataRequired, ValidationError

from app.db_models import Member


class MemberRegisterForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired("Input is required!"), DataRequired("Data is required!")])
    email = EmailField("Email",
                       validators=[InputRequired("Input is required!"),
                                   DataRequired("Data is required!")])
    password = PasswordField()
    age = SelectField("Age", choices=[(str(age), str(age)) for age in range(1, 99)])
    phone = StringField("Phone number")
    submit = SubmitField("Register")

    def validate_email(form, field):
        member = Member.query.filter_by(email=field.data).first()
        if member:
            raise ValidationError("Email already exists.")

class MemberLoginForm(FlaskForm):
    email = EmailField("Email",
                       validators=[InputRequired("Input is required!"),
                                   DataRequired("Data is required!")]
                       )
    password = PasswordField("Password",
                             validators=[InputRequired("Input is required"),
                                         DataRequired("Data is required")])
    submit = SubmitField("Login")
