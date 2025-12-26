"""
Authentication Blueprint
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, OTPToken, SystemSettings
from app.forms import LoginForm, CreateUserForm
from app.email_service import EmailService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.context_processor
def inject_globals():
    """Inject global variables into auth templates"""
    logo_filename = SystemSettings.get_setting('logo_filename', None)
    logo_url = url_for('main.serve_logo', filename=logo_filename) if logo_filename else None
    return dict(logo_url=logo_url)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Login successful
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
        flash(f'Welcome, {user.username}!', 'success')
        
        # Redirect to next page or dashboard
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new user (Admin only)"""
    if not current_user.is_admin:
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = CreateUserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('main.users'))
    
    return render_template('create_user.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Public registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, full_name, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=False  # New users are not admin by default
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'danger')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal if email exists or not (security)
            flash('If the email exists, you will receive a password reset code.', 'info')
            return render_template('forgot_password.html')
        
        # Generate OTP
        otp = OTPToken.create_otp(user.id, expiry_minutes=15)
        
        # Send email
        email_service = EmailService()
        success, message = email_service.send_otp_email(
            recipient_email=user.email,
            recipient_name=user.full_name or user.username,
            otp_code=otp.code
        )
        
        if success:
            flash('Password reset code has been sent to your email.', 'success')
            return redirect(url_for('auth.reset_password', email=email))
        else:
            flash('Failed to send email. Please contact administrator.', 'danger')
            return render_template('forgot_password.html')
    
    return render_template('forgot_password.html')

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password with OTP"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    email = request.args.get('email') or request.form.get('email')
    
    if not email:
        flash('Invalid reset link', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid reset link', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([otp_code, new_password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('reset_password.html', email=email)
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', email=email)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('reset_password.html', email=email)
        
        # Verify OTP
        valid, message, otp = OTPToken.verify_otp(user.id, otp_code)
        
        if not valid:
            flash(message, 'danger')
            return render_template('reset_password.html', email=email)
        
        # Reset password
        user.set_password(new_password)
        otp.mark_as_used()
        db.session.commit()
        
        flash('Password reset successfully! Please login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', email=email)
