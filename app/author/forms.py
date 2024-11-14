from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Length

from app.db_models import Author


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

    def set_choices(self):
        self.author.choices = [(author.id, author.name) for author in Author.query.all()]

class EditAuthorForm(DeleteAuthorForm):
    name = StringField("Edit name",
                       validators=[InputRequired("Input is required!"),
                                   DataRequired("Data is required!")])
    biography = TextAreaField("Edit biography",
                              validators=[Length(max=200, message="Biography must be maximum 00 characters long")])