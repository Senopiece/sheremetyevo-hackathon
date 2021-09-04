from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length


class RegisterForm(FlaskForm):
    login = StringField('Название компании арендатора',
                        validators=[DataRequired(message='Это обязательное поле')])
    password = PasswordField('Пароль',
                             validators=[DataRequired(message='Это обязательное поле')])
    repeat_password = PasswordField(
        'Повторите пароль', validators=[DataRequired(message='Это обязательное поле'),
                                        EqualTo('password', message='Пароли должны совпадать')]
    )
    account_address = StringField(
        'Адрес аккаунта в блокчейн-сети',
        validators=[Length(40, 42, message='Длина адреса - 40 или 42 символа')]
    )

    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
