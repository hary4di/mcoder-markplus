"""
Database Models
"""
import secrets
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class User(UserMixin, db.Model):
    """User model for authentication"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class SystemSettings(db.Model):
    """System settings model for configuration"""
    
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        """Get setting value by key"""
        setting = SystemSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set setting value"""
        setting = SystemSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'

class OTPToken(db.Model):
    """OTP token model for password reset"""
    
    __tablename__ = 'otp_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('otp_tokens', lazy='dynamic'))
    
    @staticmethod
    def generate_code():
        """Generate a random 6-digit OTP code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    @staticmethod
    def create_otp(user_id, expiry_minutes=10):
        """
        Create a new OTP token for user
        
        Args:
            user_id: User ID
            expiry_minutes: Expiration time in minutes (default 10)
            
        Returns:
            OTPToken object
        """
        # Invalidate all previous unused OTP tokens for this user
        OTPToken.query.filter_by(user_id=user_id, is_used=False).update({'is_used': True})
        
        # Generate new OTP
        code = OTPToken.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        otp = OTPToken(
            user_id=user_id,
            code=code,
            expires_at=expires_at
        )
        db.session.add(otp)
        db.session.commit()
        
        return otp
    
    @staticmethod
    def verify_otp(user_id, code):
        """
        Verify OTP code for user
        
        Args:
            user_id: User ID
            code: 6-digit OTP code
            
        Returns:
            tuple: (valid: bool, message: str, otp_object: OTPToken or None)
        """
        otp = OTPToken.query.filter_by(
            user_id=user_id,
            code=code,
            is_used=False
        ).first()
        
        if not otp:
            return False, "Invalid OTP code", None
        
        if datetime.utcnow() > otp.expires_at:
            return False, "OTP code has expired", None
        
        return True, "OTP verified successfully", otp
    
    def mark_as_used(self):
        """Mark this OTP as used"""
        self.is_used = True
        db.session.commit()
    
    def __repr__(self):
        return f'<OTPToken user_id={self.user_id} code={self.code}>'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))
