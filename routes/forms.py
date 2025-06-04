from flask_wtf import FlaskForm
# from models import db
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])

    name = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    lastname = StringField('Apellido', validators=[DataRequired(), Length(max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Length(max=120)])
    
    is_admin = BooleanField('Es administrador')
    submit = SubmitField('Registrar')

class CambiarRecuperarContraseñaForm(FlaskForm):
    username = StringField('Usuario (solo si olvidaste la contraseña)', validators=[])
    old_password = PasswordField('Contraseña actual', validators=[])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar nueva contraseña', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Cambiar contraseña')