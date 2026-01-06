"""
WTForms for Flask application
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from app.models import User

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CreateUserForm(FlaskForm):
    """Create new user form (Admin only)"""
    full_name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=120, message='Name must be 2-120 characters')
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
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')

class EditUserForm(FlaskForm):
    """Edit user form (Admin only)"""
    full_name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=120, message='Name must be 2-120 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email format')
    ])
    password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(),
        EqualTo('password', message='Passwords do not match')
    ])
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active')
    submit = SubmitField('Update User')

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
