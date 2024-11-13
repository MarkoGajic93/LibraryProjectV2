from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import EmailField, StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, DataRequired, Email, ValidationError

from db.db_service import get_db


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
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT email FROM member WHERE email=%s""", (field.data,))
        if cursor.fetchone():
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

    def validate_email(form, field):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""SELECT email FROM member WHERE email=%s""", (field.data,))
        if not cursor.fetchone():
            raise ValidationError("There is no member with that email")
