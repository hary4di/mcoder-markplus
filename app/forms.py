"""
WTForms for Flask application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be 3-80 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CreateUserForm(FlaskForm):
    """Create new user form (Admin only)"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=80, message='Username must be 3-80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Password confirmation is required'),
        EqualTo('password', message='Passwords do not match')
    ])
    is_admin = BooleanField('Admin User')
    submit = SubmitField('Create User')
    
    def validate_username(self, field):
        """Check if username already exists"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')

class ClassificationForm(FlaskForm):
    """Classification settings form"""
    data_source = SelectField('Data Source', choices=[
        ('kobo', 'Kobo API (Live Data)'),
        ('excel', 'Excel Files (Offline)')
    ], validators=[DataRequired()])
    
    max_categories = IntegerField('Maximum Categories', 
        default=10,
        validators=[DataRequired()])
    
    auto_upload = BooleanField('Auto Upload to Kobo', default=True)
    
    submit = SubmitField('Start Classification')
