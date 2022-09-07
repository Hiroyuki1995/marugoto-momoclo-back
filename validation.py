from wtforms import Form,  StringField, validators, SelectField, IntegerField

class LinkRegistrationForm(Form):
    order:int = IntegerField('order', validators=[validators.NumberRange(min=0,max=99991231)])
    # order = IntegerField('order')
    category = SelectField('category', choices=["tickets","goods"], validators=[validators.DataRequired()])
    name = StringField('name', validators=[validators.DataRequired()])
    url = StringField('url', validators=[validators.URL()])