"""
Grievance Blueprint - Student Grievance System
Integrated for BSU Kiosk System
Database: SQLite - databases/grievance.db
"""

from flask import Blueprint, render_template as flask_render_template, session, flash, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from jinja2 import TemplateNotFound
import os


def render_template(template_name, **context):
    """Render grievance templates with a safe fallback to the module landing page."""
    try:
        return flask_render_template(template_name, **context)
    except TemplateNotFound:
        fallback_context = {'title': context.get('title', 'Grievance Module')}
        return flask_render_template('module_grievance.html', **fallback_context)

# Create blueprint
grievance_bp = Blueprint('grievance', __name__,
                        template_folder='../templates/grievance',
                        static_folder='../static')

# Import db after blueprint creation to avoid circular import
from extension import db

# ============================================================================
# MODELS
# ============================================================================

class GrievanceStudent(db.Model):
    """Student model for grievance system"""
    __bind_key__ = 'grievance'
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class GrievanceAdmin(db.Model):
    """Admin model for grievance system"""
    __bind_key__ = 'grievance'
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Concern(db.Model):
    """Concern model"""
    __bind_key__ = 'grievance'
    __tablename__ = 'concerns'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(200), nullable=False)
    student_id = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(100), default='other')
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, in-progress, resolved
    priority = db.Column(db.String(20), default='normal')
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    resolved_at = db.Column(db.DateTime)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required', 'danger')
            return redirect(url_for('grievance.admin_login'))
        return f(*args, **kwargs)
    return decorated

def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'student_id' not in session:
            flash('Student login required', 'danger')
            return redirect(url_for('grievance.student_login'))
        return f(*args, **kwargs)
    return decorated

def init_default_admin():
    """Initialize default admin if not exists"""
    try:
        if not GrievanceAdmin.query.filter_by(username='admin').first():
            admin = GrievanceAdmin(
                username='admin',
                email='admin@grievance.bsu.edu',
                full_name='System Administrator'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    except:
        pass

def get_grievance_stats():
    """Get statistics for dashboard"""
    try:
        concerns = Concern.query.count()
        pending = Concern.query.filter_by(status='pending').count()
        resolved = Concern.query.filter_by(status='resolved').count()
        users = GrievanceStudent.query.count()
        return {
            'concerns': concerns,
            'pending': pending,
            'resolved': resolved,
            'users': users
        }
    except:
        return {'concerns': 0, 'pending': 0, 'resolved': 0, 'users': 0}

# ============================================================================
# ROUTES
# ============================================================================

@grievance_bp.route('/app')
@grievance_bp.route('/app/')
def home():
    """Grievance home page - redirects to login"""
    return redirect(url_for('grievance.student_login'))

# ========== STUDENT ROUTES ==========

@grievance_bp.route('/app/student-login', methods=['GET', 'POST'])
def student_login():
    """Student login with email and password"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        student = GrievanceStudent.query.filter_by(email=email).first()
        
        if student and student.check_password(password):
            session['student_id'] = student.student_id
            session['student_name'] = student.full_name
            session['student_email'] = student.email
            flash(f'Welcome back, {student.full_name}!', 'success')
            return redirect(url_for('grievance.student_dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('grievance/student_login.html', title='Student Login')

@grievance_bp.route('/app/student-register', methods=['GET', 'POST'])
def student_register():
    """Student registration"""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        if not full_name:
            errors.append('Full name is required')
        if not student_id:
            errors.append('Student ID is required')
        if not email:
            errors.append('Email is required')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if student already exists
        if GrievanceStudent.query.filter_by(student_id=student_id).first():
            errors.append('Student ID already registered')
        if GrievanceStudent.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('grievance/student_register.html', title='Register')
        
        # Create new student
        try:
            student = GrievanceStudent(
                full_name=full_name,
                student_id=student_id,
                email=email
            )
            student.set_password(password)
            db.session.add(student)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('grievance.student_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('grievance/student_register.html', title='Register')

@grievance_bp.route('/app/student-dashboard')
@student_required
def student_dashboard():
    concerns = Concern.query.filter_by(student_id=session['student_id']).all()
    return render_template('grievance/student_dashboard.html', concerns=concerns, title='Dashboard')

@grievance_bp.route('/app/submit-concern', methods=['GET', 'POST'])
@student_required
def submit_concern():
    if request.method == 'POST':
        try:
            concern = Concern(
                student_name=session['student_name'],
                student_id=session['student_id'],
                email=session['student_email'],
                category=request.form.get('category', 'other'),
                subject=request.form.get('subject'),
                description=request.form.get('description'),
                priority=request.form.get('priority', 'normal')
            )
            db.session.add(concern)
            db.session.commit()
            flash('Concern submitted successfully!', 'success')
            return redirect(url_for('grievance.student_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('grievance/submit_concern.html', title='Submit Concern')

@grievance_bp.route('/app/student-logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    session.pop('student_email', None)
    flash('Logged out', 'info')
    return redirect(url_for('grievance.student_login'))

# ========== ADMIN ROUTES ==========

@grievance_bp.route('/app/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = GrievanceAdmin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.full_name
            flash(f'Welcome {admin.full_name}!', 'success')
            return redirect(url_for('grievance.admin_dashboard'))
        
        flash('Invalid credentials', 'danger')
    
    return render_template('grievance/admin_login.html', title='Admin Login')

@grievance_bp.route('/app/admin-dashboard')
@admin_required
def admin_dashboard():
    pending = Concern.query.filter_by(status='pending').all()
    in_progress = Concern.query.filter_by(status='in-progress').all()
    resolved = Concern.query.filter_by(status='resolved').all()
    all_admins = GrievanceAdmin.query.all()
    
    return render_template('grievance/admin_dashboard.html',
                         pending=pending, in_progress=in_progress, resolved=resolved, 
                         all_admins=all_admins, title='Admin Dashboard')

@grievance_bp.route('/app/admin/add-admin', methods=['GET', 'POST'])
@admin_required
def add_admin():
    if request.method == 'POST':
        try:
            admin = GrievanceAdmin(
                username=request.form.get('username'),
                email=request.form.get('email'),
                full_name=request.form.get('full_name')
            )
            admin.set_password(request.form.get('password'))
            db.session.add(admin)
            db.session.commit()
            flash('Admin added successfully!', 'success')
            return redirect(url_for('grievance.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('grievance/add_admin.html', title='Add Admin')

@grievance_bp.route('/app/admin/concern/<int:concern_id>', methods=['GET', 'POST'])
@admin_required
def manage_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    
    if request.method == 'POST':
        try:
            concern.status = request.form.get('status')
            concern.priority = request.form.get('priority')
            concern.response = request.form.get('response')
            
            if concern.status == 'resolved':
                concern.resolved_at = datetime.now()
            
            db.session.commit()
            flash('Concern updated!', 'success')
            return redirect(url_for('grievance.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('grievance/manage_concern.html', concern=concern, title='Manage Concern')

@grievance_bp.route('/app/admin-logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Logged out', 'info')
    return redirect(url_for('grievance.admin_login'))

# Export for main app
__all__ = ['grievance_bp', 'get_grievance_stats', 'init_default_admin']
