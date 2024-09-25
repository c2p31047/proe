from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = EmailField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegisterForm(FlaskForm):
    name = StringField('名前', validators=[DataRequired()])
    email = EmailField('メールアドレス', validators=[DataRequired(), Email()])
    postal_code = StringField('郵便番号', validators=[Length(min=7, max=7)])
    address = StringField('住所')
    phonenumber = StringField('電話番号', validators=[Length(min=10, max=20)])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('登録')
