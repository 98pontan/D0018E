from wtforms import Form, StringField, SubmitField

from wtforms.validators import InputRequired, Length, Email

class MakeReview(Form):
    rating = StringField('Rate between 1 to 5', validators=[Length(min=1, max=1), InputRequired()])
    review = StringField('Write a review:', validators=[Length(min=1, max=500), InputRequired()])
    submit = SubmitField('Upload')