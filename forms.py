from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Post Title", validators=[DataRequired()])
    body = StringField("body", validators=[DataRequired()])
    img_url = StringField("post Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField("add Post")
