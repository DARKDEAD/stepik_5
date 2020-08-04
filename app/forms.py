from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email
from wtforms.validators import InputRequired
from wtforms.validators import Length


class AuthForm(FlaskForm):
    mail = StringField("mail", [InputRequired(), Email()])
    password = PasswordField(
            "password",
            [InputRequired(), Length(min=6, message="Минимальная пароля 6 знаков")],
    )
    name = StringField("name")


class UserCartForm(FlaskForm):
    name = StringField("name", [InputRequired()])
    address = StringField("address", [InputRequired()])
    mail = StringField("mail", [Email()])
    phone = StringField(
            "phone",
            [InputRequired(), Length(min=6, message="Минимальная длина номера 6 знаков")],
    )
