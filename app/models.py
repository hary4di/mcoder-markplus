"""
Database Models
"""
import secrets
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

class Company(db.Model):
    """Company model for multi-tenant support"""
    
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Company-specific logo
    logo_filename = db.Column(db.String(255))
    
    # Company-specific email settings (Brevo)
    brevo_api_key = db.Column(db.String(255))
    brevo_sender_email = db.Column(db.String(120))
    brevo_sender_name = db.Column(db.String(100))
    
    # Company-specific AI settings
    openai_api_key = db.Column(db.String(255))
    openai_model = db.Column(db.String(50), default='gpt-4o-mini')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'

class User(UserMixin, db.Model):
    """User model for authentication"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    password_hash = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.String(255))  # Profile photo filename
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Company relationship (Multi-tenant)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False, default=1)
    
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
    
    @property
    def is_super_admin(self):
        """Check if user is super admin (email ends with @markplusinc.com and is admin)"""
        return self.is_admin and self.email and self.email.endswith('@markplusinc.com')
    
    @property
    def role_name(self):
        """Get user role name"""
        if self.is_super_admin:
            return 'Super Admin'
        elif self.is_admin:
            return 'Admin'
        else:
            return 'User'
    
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
    
    @staticmethod
    def get_settings():
        """Get all settings as an object with properties"""
        class SettingsObject:
            def __init__(self):
                self.app_name = SystemSettings.get_setting('app_name', 'M-Code Pro')
                self.logo_filename = SystemSettings.get_setting('logo_filename', None)
                self.brevo_api_key = SystemSettings.get_setting('brevo_api_key', None)
                self.brevo_sender_email = SystemSettings.get_setting('brevo_sender_email', None)
                self.brevo_sender_name = SystemSettings.get_setting('brevo_sender_name', 'M-Code Pro')
        
        return SettingsObject()
    
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

class ClassificationJob(db.Model):
    """Classification job tracking with database persistence"""
    
    __tablename__ = 'classification_jobs'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID
    task_id = db.Column(db.String(36), index=True)  # Celery task ID
    
    # User & Metadata
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_type = db.Column(db.String(20), nullable=False)  # 'open_ended' or 'semi_open'
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, error
    
    # Input Files
    original_kobo_filename = db.Column(db.String(255))
    original_raw_filename = db.Column(db.String(255))
    input_kobo_path = db.Column(db.String(500))  # Timestamped input file
    input_raw_path = db.Column(db.String(500))   # Timestamped input file
    
    # Output Files (NEW: timestamped outputs, not overwriting inputs)
    output_kobo_filename = db.Column(db.String(255))
    output_raw_filename = db.Column(db.String(255))
    output_kobo_path = db.Column(db.String(500))
    output_raw_path = db.Column(db.String(500))
    
    # Classification Settings (JSON)
    settings = db.Column(db.Text)  # JSON: {max_categories, confidence_threshold, mode, etc}
    
    # Progress Tracking
    progress = db.Column(db.Integer, default=0)  # 0-100
    current_step = db.Column(db.String(255))
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Results Summary (JSON)
    results_summary = db.Column(db.Text)  # JSON: {total_variables, duration, etc}
    error_message = db.Column(db.Text)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('classification_jobs', lazy='dynamic'))
    variables = db.relationship('ClassificationVariable', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def duration_seconds(self):
        """Calculate job duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_download_available(self):
        """Check if download is still available (24 hours from completion)"""
        if not self.completed_at:
            return False
        
        import pytz
        wib = pytz.timezone('Asia/Jakarta')
        now_wib = datetime.now(wib)
        completed_wib = self.completed_at.replace(tzinfo=pytz.UTC).astimezone(wib)
        
        hours_elapsed = (now_wib - completed_wib).total_seconds() / 3600
        return hours_elapsed < 24
    
    @property
    def download_expires_at(self):
        """Get download expiration time in WIB"""
        if not self.completed_at:
            return None
        
        import pytz
        from datetime import timedelta
        wib = pytz.timezone('Asia/Jakarta')
        completed_wib = self.completed_at.replace(tzinfo=pytz.UTC).astimezone(wib)
        return completed_wib + timedelta(hours=24)
    
    @property
    def hours_until_expiry(self):
        """Get hours remaining until download expiry"""
        if not self.completed_at:
            return None
        
        import pytz
        wib = pytz.timezone('Asia/Jakarta')
        now_wib = datetime.now(wib)
        completed_wib = self.completed_at.replace(tzinfo=pytz.UTC).astimezone(wib)
        
        hours_elapsed = (now_wib - completed_wib).total_seconds() / 3600
        hours_remaining = 24 - hours_elapsed
        return max(0, hours_remaining)  # Never negative
    
    @property
    def total_variables(self):
        """Get total number of variables classified"""
        return self.variables.count()
    
    @property
    def total_responses(self):
        """Get total number of responses processed across all variables"""
        total = 0
        for var in self.variables:
            total += (var.total_responses or 0)
        return total
    
    @property
    def total_categories(self):
        """Get total number of categories generated"""
        total = 0
        for var in self.variables:
            total += (var.categories_generated or 0)
        return total
    
    @property
    def original_filename(self):
        """Get original filename for display"""
        return self.original_raw_filename or self.original_kobo_filename or 'Unknown'
    
    @property
    def classification_type(self):
        """Get classification type from job_type"""
        return self.job_type or 'pure_open_ended'
    
    @property
    def completed_at_wib(self):
        """Get completion time in WIB timezone"""
        if not self.completed_at:
            return None
        
        import pytz
        wib = pytz.timezone('Asia/Jakarta')
        return self.completed_at.replace(tzinfo=pytz.UTC).astimezone(wib)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        import json
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_type': self.job_type,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration_seconds,
            'progress': self.progress,
            'settings': json.loads(self.settings) if self.settings else {},
            'results_summary': json.loads(self.results_summary) if self.results_summary else {},
            'variables': [v.to_dict() for v in self.variables],
            'output_files': {
                'kobo': self.output_kobo_filename,
                'raw': self.output_raw_filename
            }
        }
    
    def __repr__(self):
        return f'<ClassificationJob {self.job_id} - {self.status}>'


class ClassificationVariable(db.Model):
    """Individual variable classification results"""
    
    __tablename__ = 'classification_variables'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('classification_jobs.id'), nullable=False, index=True)
    
    # Variable Info
    variable_name = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text)
    
    # Classification Results
    categories_generated = db.Column(db.Integer)
    total_responses = db.Column(db.Integer)
    valid_classified = db.Column(db.Integer)
    invalid_count = db.Column(db.Integer)
    empty_count = db.Column(db.Integer)
    
    # Categories Detail (JSON)
    categories = db.Column(db.Text)  # JSON: [{category, code, count, percentage}]
    
    # Timing
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, error
    error_message = db.Column(db.Text)
    
    @property
    def duration_seconds(self):
        """Calculate variable processing duration"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        import json
        return {
            'variable_name': self.variable_name,
            'question_text': self.question_text,
            'categories_generated': self.categories_generated,
            'total_responses': self.total_responses,
            'valid_classified': self.valid_classified,
            'invalid_count': self.invalid_count,
            'empty_count': self.empty_count,
            'categories': json.loads(self.categories) if self.categories else [],
            'status': self.status,
            'duration': self.duration_seconds
        }
    
    def __repr__(self):
        return f'<ClassificationVariable {self.variable_name}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))
