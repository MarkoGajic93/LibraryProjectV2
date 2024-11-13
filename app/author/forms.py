from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Length


class NewAuthorForm(FlaskForm):
    name = StringField("Name",
                        validators=[InputRequired("Input is required!"),
                                    DataRequired("Data is required!")])

    biography = TextAreaField("Biography",
                              validators=[Length(max=200, message="Biography must be maximum 200 characters long")])

    submit = SubmitField("Add author")

class DeleteAuthorForm(FlaskForm):
    author = SelectField("Author")
    submit = SubmitField("Submit")

    def set_choices(self, cursor):
        cursor.execute(f"SELECT id, name FROM author")
        options = cursor.fetchall()
        self.author.choices = options

class EditAuthorForm(DeleteAuthorForm):
    name = StringField("Edit name",
                       validators=[InputRequired("Input is required!"),
                                   DataRequired("Data is required!")])
    biography = TextAreaField("Edit biography",
                              validators=[Length(max=200, message="Biography must be maximum 00 characters long")])