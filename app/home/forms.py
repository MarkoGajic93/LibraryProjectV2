from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, SubmitField


class FilterForm(FlaskForm):
    title = StringField("Title")
    author = SelectField("Author")
    year_published = SelectField("Year published", choices=[(0, "---"), (1, "Newest first"), (2, "Oldest first")])
    submit = SubmitField("Filter")