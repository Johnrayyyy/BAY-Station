"""
LostLink Blueprint - Lost and Found Management System
Integrated for BSU Kiosk System
Database: SQLite - databases/lostlink.db
"""

from flask import Blueprint, render_template as flask_render_template, session, flash, redirect, url_for, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from jinja2 import TemplateNotFound
import os


def render_template(template_name, **context):
    """Render LostLink templates with a safe fallback to the module landing page."""
    try:
        return flask_render_template(template_name, **context)
    except TemplateNotFound:
        fallback_context = {'title': context.get('title', 'LostLink Module')}
        return flask_render_template('module_lostlink.html', **fallback_context)

# Create blueprint
lostlink_bp = Blueprint('lostlink', __name__, 
                       template_folder='../templates/lostlink',
                       static_folder='../static')

# Import db AFTER blueprint is created (lazy import)
from extension import db, mail

# ============================================================================
# MODELS
# ============================================================================

class Register(db.Model):
    __bind_key__ = 'lostlink'
    __tablename__ = 'users'

    sr_code = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    surname = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)

class Report(db.Model):
    __bind_key__ = 'lostlink'
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(255), nullable=False)
    place = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    report_by = db.Column(
        db.String(255),
        db.ForeignKey('users.sr_code'),
        nullable=True
    )

class Return(db.Model):
    __bind_key__ = 'lostlink'
    __tablename__ = 'returns'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('reports.id', ondelete='CASCADE'), nullable=False)
    item_name = db.Column(db.String(255), nullable=False)
    place_found = db.Column(db.String(255), nullable=False)
    photo = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    claimed_by = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    timestamp_claimed = db.Column(db.DateTime, default=datetime.now)

class LostLinkAdmin(db.Model):
    """LostLink Admin model for authentication and management"""
    __bind_key__ = 'lostlink'
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'sr_code' not in session:
            flash('You must be logged in to access this page.', 'danger')
            return redirect(url_for('lostlink.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_lostlink_stats():
    """Get statistics for dashboard"""
    try:
        reports_count = Report.query.count()
        returns_count = Return.query.count()
        users_count = Register.query.count()
        return {
            'reports': reports_count,
            'returns': returns_count,
            'users': users_count
        }
    except:
        return {'reports': 0, 'returns': 0, 'users': 0}

# ============================================================================
# ROUTES
# ============================================================================

@lostlink_bp.route('/app')
@lostlink_bp.route('/app/')
def home():
    """LostLink home page"""
    return render_template('lostlink/home.html', title='LOSTLINK')

@lostlink_bp.route('/app/register', methods=['GET', 'POST'])
def register():
    """Student registration"""
    if request.method == 'POST':
        try:
            sr_code = request.form.get('sr_code')
            username = request.form.get('username')
            
            # Check for existing user
            existing_sr = Register.query.filter_by(sr_code=sr_code).first()
            if existing_sr:
                flash("Sr-Code already registered!", "danger")
                return render_template('lostlink/register.html', title='Register')
            
            existing_user = Register.query.filter_by(username=username).first()
            if existing_user:
                flash("Username already taken!", "danger")
                return render_template('lostlink/register.html', title='Register')

            hashed_password = generate_password_hash(request.form.get('password'))

            new_user = Register(
                sr_code=sr_code,
                name=request.form.get('name'),
                surname=request.form.get('surname'),
                age=int(request.form.get('age')),
                email=request.form.get('email'),
                contact=request.form.get('contact'),
                gender=request.form.get('gender'),
                username=username,
                password=hashed_password,
                role="student"
            )

            db.session.add(new_user)
            db.session.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('lostlink.login'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Registration error: {str(e)}", "danger")
    
    return render_template('lostlink/register.html', title='Register')

@lostlink_bp.route('/app/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Register.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['sr_code'] = user.sr_code
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.role == "admin":
                return redirect(url_for('lostlink.admin'))
            return redirect(url_for('lostlink.dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('lostlink/login.html', title='Login')

@lostlink_bp.route('/app/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('lostlink.home'))

@lostlink_bp.route('/app/dashboard')
@login_required
def dashboard():
    """Student dashboard"""
    reports = Report.query.all()
    return render_template('lostlink/dashboard.html', reports=reports, title='Dashboard')

@lostlink_bp.route('/app/dashboard/report', methods=['GET', 'POST'])
@login_required
def report_item():
    """Report lost item"""
    if request.method == 'POST':
        try:
            photo = request.files.get('photo')
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo.save(filepath)

                new_report = Report(
                    item=request.form.get('item'),
                    place=request.form.get('place'),
                    photo=filename,
                    description=request.form.get('description'),
                    report_by=session.get('sr_code')
                )

                db.session.add(new_report)
                db.session.commit()
                flash('Item reported successfully!', 'success')
                return redirect(url_for('lostlink.dashboard'))
            else:
                flash('Invalid file format. Please upload an image.', 'danger')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error reporting item: {str(e)}', 'danger')
    
    return render_template('lostlink/report.html', title='Report Item')

@lostlink_bp.route('/app/admin')
@login_required
def admin():
    """Admin dashboard"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('lostlink.dashboard'))
    
    reports = Report.query.all()
    returns = Return.query.all()
    return render_template('lostlink/admin.html', reports=reports, returns=returns, title='Admin')

@lostlink_bp.route('/app/admin/returning/<int:item_id>', methods=['GET', 'POST'])
@login_required
def returning(item_id):
    """Process item return"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('lostlink.dashboard'))
    
    report = Report.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            photo = request.files.get('photo')
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo.save(filepath)

                new_return = Return(
                    item_id=item_id,
                    item_name=report.item,
                    place_found=request.form.get('place_found'),
                    photo=filename,
                    description=request.form.get('description'),
                    claimed_by=request.form.get('claimed_by'),
                    email=request.form.get('email'),
                    contact=request.form.get('contact')
                )

                db.session.add(new_return)
                db.session.delete(report)
                db.session.commit()

                # Send email notification
                try:
                    msg = Message(
                        subject='Item Found - LostLink',
                        recipients=[new_return.email],
                        body=f'Your lost item "{new_return.item_name}" has been found and is ready for claiming.'
                    )
                    mail.send(msg)
                except:
                    pass

                flash('Item marked as returned successfully!', 'success')
                return redirect(url_for('lostlink.admin'))
            else:
                flash('Invalid file format. Please upload an image.', 'danger')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing return: {str(e)}', 'danger')
    
    return render_template('lostlink/returning.html', report=report, title='Return Item')

@lostlink_bp.route('/app/admin/returned')
@login_required
def returned():
    """View returned items"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('lostlink.dashboard'))
    
    returns = Return.query.all()
    return render_template('lostlink/returned.html', returns=returns, title='Returned Items')

@lostlink_bp.route('/app/update/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update(item_id):
    """Update report"""
    report = Report.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            report.item = request.form.get('item')
            report.place = request.form.get('place')
            report.description = request.form.get('description')
            
            photo = request.files.get('photo')
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo.save(filepath)
                report.photo = filename

            db.session.commit()
            flash('Report updated successfully!', 'success')
            return redirect(url_for('lostlink.dashboard'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating report: {str(e)}', 'danger')
    
    return render_template('lostlink/update.html', report=report, title='Update Report')

@lostlink_bp.route('/app/delete/<int:item_id>', methods=['POST'])
@login_required
def delete(item_id):
    """Delete report"""
    try:
        report = Report.query.get_or_404(item_id)
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting report: {str(e)}', 'danger')
    
    return redirect(url_for('lostlink.admin'))

# ============================================================================
# ADMIN AUTHENTICATION & MANAGEMENT
# ============================================================================

@lostlink_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = LostLinkAdmin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['lostlink_admin_id'] = admin.id
            session['lostlink_admin_name'] = admin.full_name
            flash(f'Welcome back, {admin.full_name}!', 'success')
            return redirect(url_for('lostlink.admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('lostlink/admin_login.html', title='Admin Login')

@lostlink_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'lostlink_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('lostlink.admin_login'))
    
    try:
        # Query all reports and returns from database with explicit bind_key
        total_reports = db.session.query(Report).count()
        total_returned = db.session.query(Return).count()
        recent_reports = db.session.query(Report).order_by(Report.timestamp.desc()).limit(10).all()
        recent_returns = db.session.query(Return).order_by(Return.timestamp_claimed.desc()).limit(10).all()
        
        # Calculate pending items (reports that haven't been returned)
        pending = max(0, total_reports - total_returned)
        
        # Calculate success rate with safe division
        if total_reports > 0:
            success_rate = round((total_returned / total_reports) * 100, 1)
        else:
            success_rate = 0
        
        stats = {
            'total_reports': total_reports,
            'total_returned': total_returned,
            'pending': pending,
            'success_rate': success_rate,
            'recent_reports': recent_reports,
            'recent_returns': recent_returns
        }
        
        return render_template('lostlink/admin_dashboard.html', stats=stats, admin_name=session.get('lostlink_admin_name'), title='Admin Dashboard')
    except Exception as e:
        # Log error and return default stats
        print(f"Dashboard Error: {str(e)}")
        flash('Error loading dashboard data. Showing default values.', 'warning')
        stats = {
            'total_reports': 0,
            'total_returned': 0,
            'pending': 0,
            'success_rate': 0,
            'recent_reports': [],
            'recent_returns': []
        }
        return render_template('lostlink/admin_dashboard.html', stats=stats, admin_name=session.get('lostlink_admin_name'), title='Admin Dashboard')

@lostlink_bp.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('lostlink_admin_id', None)
    session.pop('lostlink_admin_name', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('lostlink.admin_login'))

@lostlink_bp.route('/admin/reports')
def admin_reports():
    """Manage lost and found reports"""
    if 'lostlink_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('lostlink.admin_login'))
    
    reports = db.session.query(Report).order_by(Report.timestamp.desc()).all()
    return render_template('lostlink/admin_reports.html', reports=reports, admin_name=session.get('lostlink_admin_name'), title='Manage Reports')

@lostlink_bp.route('/admin/report/<int:report_id>/delete', methods=['POST'])
def admin_delete_report(report_id):
    """Delete report"""
    if 'lostlink_admin_id' not in session:
        return redirect(url_for('lostlink.admin_login'))
    
    try:
        report = Report.query.get_or_404(report_id)
        db.session.delete(report)
        db.session.commit()
        flash('Report deleted successfully', 'success')
    except:
        flash('Error deleting report', 'danger')
    
    return redirect(url_for('lostlink.admin_reports'))

@lostlink_bp.route('/admin/report/<int:report_id>/mark-returned', methods=['POST'])
def admin_mark_returned(report_id):
    """Mark report as returned/claimed"""
    if 'lostlink_admin_id' not in session:
        return redirect(url_for('lostlink.admin_login'))
    
    try:
        report = Report.query.get_or_404(report_id)
        claimed_by = request.form.get('claimed_by', 'Unknown')
        email = request.form.get('email', '')
        contact = request.form.get('contact', '')
        
        returned_item = Return(
            item_id=report.id,
            item_name=report.item,
            place_found=report.place,
            photo=report.photo,
            description=report.description,
            claimed_by=claimed_by,
            email=email,
            contact=contact
        )
        db.session.add(returned_item)
        db.session.commit()
        flash(f'Item marked as returned/claimed by {claimed_by}', 'success')
    except Exception as e:
        flash(f'Error marking as returned: {str(e)}', 'danger')
    
    return redirect(url_for('lostlink.admin_reports'))

@lostlink_bp.route('/admin/returns')
def admin_returns():
    """View all returned/claimed items"""
    if 'lostlink_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('lostlink.admin_login'))
    
    returns = db.session.query(Return).order_by(Return.timestamp_claimed.desc()).all()
    return render_template('lostlink/admin_returns.html', returns=returns, admin_name=session.get('lostlink_admin_name'), title='Returned Items')

@lostlink_bp.route('/admin/return/<int:return_id>/delete', methods=['POST'])
def admin_delete_return(return_id):
    """Delete a returned item record"""
    if 'lostlink_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('lostlink.admin_login'))
    
    returned = Return.query.get_or_404(return_id)
    db.session.delete(returned)
    db.session.commit()
    flash(f'Return record for "{returned.item_name}" has been deleted', 'success')
    return redirect(url_for('lostlink.admin_returns'))

# Export for main app
__all__ = ['lostlink_bp', 'Register', 'Report', 'Return', 'LostLinkAdmin', 'get_lostlink_stats']
