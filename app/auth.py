"""
Authentication Blueprint
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, OTPToken, SystemSettings
from app.forms import LoginForm, CreateUserForm, EditUserForm
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
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Login successful
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
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
        # Generate username from email (before @)
        username = form.email.data.split('@')[0]
        
        # Ensure username is unique
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User(
            username=username,
            email=form.email.data,
            full_name=form.full_name.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.full_name} created successfully!', 'success')
        return redirect(url_for('main.users'))
    
    return render_template('create_user.html', form=form)

@auth_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit user (Admin only)"""
    if not current_user.is_admin:
        flash('You do not have access to this page', 'danger')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent non-super admin from editing super admin
    if user.is_super_admin and not current_user.is_super_admin:
        flash('Only Super Admin can edit Super Admin accounts', 'danger')
        return redirect(url_for('main.users'))
    form = EditUserForm()
    
    if form.validate_on_submit():
        # Check if email changed and already exists
        if form.email.data != user.email:
            existing = User.query.filter_by(email=form.email.data).first()
            if existing:
                flash('Email already exists', 'danger')
                return render_template('edit_user.html', form=form, user=user)
        
        # Update user fields
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        
        # Update password only if provided
        if form.password.data:
            user.set_password(form.password.data)
        
        # Update username if email changed
        if form.email.data != user.email:
            username = form.email.data.split('@')[0]
            counter = 1
            original_username = username
            while User.query.filter(User.username == username, User.id != user_id).first():
                username = f"{original_username}{counter}"
                counter += 1
            user.username = username
        
        db.session.commit()
        flash(f'User {user.full_name} updated successfully!', 'success')
        return redirect(url_for('main.users'))
    
    # Pre-populate form with current values
    if request.method == 'GET':
        form.full_name.data = user.full_name
        form.email.data = user.email
        form.is_admin.data = user.is_admin
        form.is_active.data = user.is_active
    
    return render_template('edit_user.html', form=form, user=user)

@auth_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete user (Admin only)"""
    try:
        if not current_user.is_admin:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'You cannot delete your own account'}), 400
        
        # Prevent non-super admin from deleting super admin
        if user.is_super_admin and not current_user.is_super_admin:
            return jsonify({'success': False, 'message': 'Only Super Admin can delete Super Admin accounts'}), 403
        
        username = user.full_name or user.username
        
        # Delete related OTP tokens first
        OTPToken.query.filter_by(user_id=user.id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'User {username} deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {e}")
        return jsonify({'success': False, 'message': f'Error deleting user: {str(e)}'}), 500

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Public registration page with OTP verification"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([email, full_name, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Generate username from email (before @)
        username = email.split('@')[0]
        
        # Ensure username is unique
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Create new user (INACTIVE until OTP verified)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=False,
            is_active=False  # User INACTIVE until email verified
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Flush to generate user.id WITHOUT full commit
        
        # Generate OTP (user.id now available)
        otp = OTPToken.create_otp(user.id, expiry_minutes=15)
        
        db.session.commit()  # Commit both user and OTP together
        
        # Send verification email
        email_service = EmailService()
        success, message = email_service.send_registration_otp(
            recipient_email=user.email,
            recipient_name=user.full_name,
            otp_code=otp.code
        )
        
        if success:
            flash('Verification code sent to your email. Please check your inbox.', 'success')
            return redirect(url_for('auth.verify_registration', email=email))
        else:
            # Rollback if email failed
            db.session.rollback()
            flash(f'Failed to send verification email: {message}', 'danger')
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/verify-registration', methods=['GET', 'POST'])
def verify_registration():
    """Verify email with OTP code"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    email = request.args.get('email') or request.form.get('email')
    
    if not email:
        flash('Invalid verification link', 'danger')
        return redirect(url_for('auth.register'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('auth.register'))
    
    # If already active, redirect to login
    if user.is_active:
        flash('Account already verified. Please login.', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp_code')
        
        if not otp_code:
            flash('Verification code is required', 'danger')
            return render_template('verify_registration_simple.html', email=email)
        
        # Verify OTP
        valid, message, otp = OTPToken.verify_otp(user.id, otp_code)
        
        if not valid:
            flash(message, 'danger')
            return render_template('verify_registration_simple.html', email=email)
        
        # Activate user account
        user.is_active = True
        otp.mark_as_used()
        db.session.commit()
        
        flash('Email verified successfully! You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('verify_registration_simple.html', email=email)

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP code for registration verification"""
    email = request.form.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Generate new OTP
    otp = OTPToken.create_otp(user.id, expiry_minutes=15)
    
    # Send email (use registration OTP for registration flow)
    email_service = EmailService()
    success, message = email_service.send_registration_otp(
        recipient_email=user.email,
        recipient_name=user.full_name,
        otp_code=otp.code
    )
    
    if success:
        return jsonify({'success': True, 'message': 'New verification code sent to your email'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send email'}), 500

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
