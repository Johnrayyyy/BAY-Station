"""
BSU LIPA SMART KIOSK - COMPLETE INTEGRATED SYSTEM
Consolidates LostLink, RGO, and Grievance modules into ONE Flask app
Running on a single port (5000) with all databases properly configured
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_cors import CORS
from flask_login import LoginManager
from extension import db, mail
from datetime import datetime, timedelta
import sys
import os

# Initialize main Flask app
app = Flask(__name__)
app.secret_key = 'bsu-smart-kiosk-unified-2026-secure-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Enable CORS for API routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================================
# DATABASE CONFIGURATIONS - SQLite
# ============================================================================

# SQLite database files
SQLITE_DIR = os.path.join(BASE_DIR, 'databases')
os.makedirs(SQLITE_DIR, exist_ok=True)

# LostLink Database (SQLite)
app.config['LOSTLINK_DB_URI'] = f'sqlite:///{os.path.join(SQLITE_DIR, "lostlink.db")}'

# RGO Database (SQLite)
app.config['RGO_DB_URI'] = f'sqlite:///{os.path.join(SQLITE_DIR, "rgo.db")}'

# Grievance Database (SQLite)
app.config['GRIEVANCE_DB_URI'] = f'sqlite:///{os.path.join(SQLITE_DIR, "grievance.db")}'

# Main database (use LostLink as default)
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['LOSTLINK_DB_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database binds for multiple databases
app.config['SQLALCHEMY_BINDS'] = {
    'lostlink': app.config['LOSTLINK_DB_URI'],
    'rgo': app.config['RGO_DB_URI'],
    'grievance': app.config['GRIEVANCE_DB_URI']
}

# Mail configuration (for LostLink email features)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lostlink.official@gmail.com'
app.config['MAIL_PASSWORD'] = 'izhu jksj gqfs ilcj'
app.config['MAIL_DEFAULT_SENDER'] = 'lostlink.official@gmail.com'

# Upload folders
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions with the Flask app
# Use init_app() to initialize the db and mail instances from extension.py
db.init_app(app)
mail.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'rgo.login'

# ============================================================================
# SAMPLE DATA FOR DASHBOARD AND CALENDAR
# ============================================================================

events = [
    {"id": 1, "title": "Midterm Examinations", "date": "2026-03-10", "category": "academic", "description": "University-wide midterm exams"},
    {"id": 2, "title": "Foundation Day", "date": "2026-03-15", "category": "social", "description": "Annual BSU Lipa Foundation Day celebration"},
    {"id": 3, "title": "Student Assembly", "date": "2026-03-20", "category": "administrative", "description": "Monthly student council assembly"},
    {"id": 4, "title": "Basketball Tournament", "date": "2026-03-25", "category": "sports", "description": "Inter-college basketball championship"},
    {"id": 5, "title": "Career Fair", "date": "2026-04-05", "category": "academic", "description": "Job and internship opportunities expo"},
]

activities = [
    {"date": "2026-03-06", "module": "LostLink", "activity": "Lost phone reported", "user": "Student-001", "status": "Active"},
    {"date": "2026-03-06", "module": "RGO", "activity": "Certificate request", "user": "Student-042", "status": "Pending"},
    {"date": "2026-03-05", "module": "Grievance", "activity": "Facility complaint", "user": "Student-123", "status": "Resolved"},
    {"date": "2026-03-05", "module": "LostLink", "activity": "Wallet returned", "user": "Student-088", "status": "Completed"},
    {"date": "2026-03-04", "module": "RGO", "activity": "Grade inquiry", "user": "Student-201", "status": "Pending"},
]

# ============================================================================
# MAIN KIOSK ROUTES (Dashboard, Map, Calendar)
# ============================================================================

@app.route("/")
def dashboard():
    """Main unified dashboard"""
    return render_template("dashboard.html")

@app.route("/map")
def map_view():
    """3D Campus Map"""
    return render_template("map.html")

@app.route("/calendar")
def calendar():
    """Interactive Student Calendar"""
    return render_template("calendar.html")

# ============================================================================
# MODULE LANDING PAGES
# ============================================================================

@app.route("/lostlink")
def lostlink_home():
    """LostLink Module Landing Page"""
    return render_template("module_lostlink.html")

@app.route("/rgo")
def rgo_home():
    """RGO Module Landing Page"""
    return render_template("module_rgo.html")

@app.route("/grievance")
def grievance_home():
    """Grievance Module Landing Page"""
    return render_template("module_grievance.html")

# ============================================================================
# DASHBOARD API ENDPOINTS
# ============================================================================

@app.route("/api/stats")
def get_stats():
    """Get dashboard statistics"""
    try:
        # Try to get real data from databases
        from blueprints.lostlink_bp import get_lostlink_stats
        from blueprints.rgo_bp import get_rgo_stats
        from blueprints.grievance_bp import get_grievance_stats
        
        lostlink_stats = get_lostlink_stats()
        rgo_stats = get_rgo_stats()
        grievance_stats = get_grievance_stats()
        
        return jsonify({
            "lostItems": lostlink_stats.get('reports', 0),
            "rgoRequests": rgo_stats.get('orders', 0),
            "grievances": grievance_stats.get('concerns', 0),
            "totalUsers": lostlink_stats.get('users', 0) + rgo_stats.get('users', 0) + grievance_stats.get('users', 0)
        })
    except:
        # Fallback to sample data
        return jsonify({
            "lostItems": 127,
            "rgoRequests": 93,
            "grievances": 38,
            "totalUsers": 1542
        })

@app.route("/api/activity-data")
def get_activity_data():
    """Get monthly activity data for charts"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    return jsonify({
        "labels": months,
        "lostlink": [45, 52, 48, 61, 55, 49],
        "rgo": [32, 38, 41, 35, 42, 39],
        "grievance": [12, 15, 18, 14, 16, 13]
    })

@app.route("/api/module-usage")
def get_module_usage():
    """Get module usage distribution"""
    return jsonify({
        "labels": ["LostLink", "RGO", "Grievance"],
        "data": [127, 93, 38]
    })

@app.route("/api/weekly-trends")
def get_weekly_trends():
    """Get weekly trend data"""
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return jsonify({
        "labels": days,
        "data": [23, 31, 28, 35, 29, 18, 12]
    })

@app.route("/api/status-breakdown")
def get_status_breakdown():
    """Get status breakdown"""
    return jsonify({
        "labels": ["Active", "Pending", "Resolved", "Completed"],
        "data": [45, 67, 89, 57]
    })

@app.route("/api/activities")
def get_activities():
    """Get recent activities"""
    return jsonify(activities)

# ============================================================================
# CALENDAR API ENDPOINTS
# ============================================================================

@app.route("/api/events")
def get_events():
    """Get all calendar events"""
    return jsonify(events)

@app.route("/api/events", methods=['POST'])
def add_event():
    """Add a new calendar event"""
    data = request.json
    new_event = {
        "id": len(events) + 1,
        "title": data['title'],
        "date": data['date'],
        "category": data['category'],
        "description": data.get('description', '')
    }
    events.append(new_event)
    return jsonify(new_event), 201

@app.route("/api/events/<int:event_id>", methods=['PUT'])
def update_event(event_id):
    """Update a calendar event"""
    global events
    data = request.json
    for event in events:
        if event['id'] == event_id:
            event['title'] = data.get('title', event['title'])
            event['date'] = data.get('date', event['date'])
            event['category'] = data.get('category', event['category'])
            event['description'] = data.get('description', event['description'])
            return jsonify(event)
    return jsonify({"error": "Event not found"}), 404

@app.route("/api/events/<int:event_id>", methods=['DELETE'])
def delete_event(event_id):
    """Delete a calendar event"""
    global events
    events = [e for e in events if e['id'] != event_id]
    return jsonify({"success": True})

# ============================================================================
# MODULE INTEGRATION
# ============================================================================

print("\n" + "="*70)
print("BSU LIPA SMART KIOSK - INITIALIZING MODULES")
print("="*70)

# Import and register LostLink blueprint
try:
    from blueprints.lostlink_bp import lostlink_bp
    app.register_blueprint(lostlink_bp, url_prefix='/lostlink')
    print("[OK] LostLink module loaded successfully")
except Exception as e:
    print(f"[ERROR] LostLink module failed: {e}")

# Import and register RGO blueprint
try:
    from blueprints.rgo_bp import rgo_bp
    app.register_blueprint(rgo_bp, url_prefix='/rgo')
    print("[OK] RGO module loaded successfully")
except Exception as e:
    print(f"[ERROR] RGO module failed: {e}")

# Import and register Grievance blueprint
try:
    from blueprints.grievance_bp import grievance_bp, init_default_admin
    app.register_blueprint(grievance_bp, url_prefix='/grievance')
    # Initialize default admin
    with app.app_context():
        init_default_admin()
    print("[OK] Grievance module loaded successfully")
except Exception as e:
    print(f"[ERROR] Grievance module failed: {e}")

# Import and register Grievance API routes
try:
    from blueprints.grievance_api import auth_bp, concern_bp, user_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(concern_bp, url_prefix='/api/concerns')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    print("[OK] Grievance API routes loaded successfully")
except Exception as e:
    print(f"[ERROR] Grievance API routes failed: {e}")

# ============================================================================
# CONTEXT PROCESSOR - LOGIN/GUEST STATUS TRACKING
# ============================================================================

@app.context_processor
def inject_user_status():
    """Inject user login status into all templates"""
    user_status = {
        'is_logged_in': False,
        'user_name': None,
        'user_module': None,
        'is_admin': False,
        'is_guest': True
    }
    
    # Check LostLink student login
    if 'username' in session and 'sr_code' in session:
        user_status['is_logged_in'] = True
        user_status['is_guest'] = False
        user_status['user_name'] = session.get('username')
        user_status['user_module'] = 'LostLink'
        user_status['is_admin'] = session.get('role') == 'admin'
        return {'user_status': user_status}
    
    # Check LostLink admin login
    if 'lostlink_admin_id' in session:
        user_status['is_logged_in'] = True
        user_status['is_guest'] = False
        user_status['user_name'] = session.get('lostlink_admin_name', 'Admin')
        user_status['user_module'] = 'LostLink'
        user_status['is_admin'] = True
        return {'user_status': user_status}
    
    # Check RGO user login (Flask-Login)
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        user_status['is_logged_in'] = True
        user_status['is_guest'] = False
        user_status['user_name'] = current_user.name if hasattr(current_user, 'name') else str(current_user)
        user_status['user_module'] = 'RGO'
        user_status['is_admin'] = hasattr(current_user, 'role') and current_user.role in ('staff', 'admin')
        return {'user_status': user_status}
    
    # Check RGO admin login
    if 'rgo_admin_id' in session:
        user_status['is_logged_in'] = True
        user_status['is_guest'] = False
        user_status['user_name'] = session.get('rgo_admin_name', 'Admin')
        user_status['user_module'] = 'RGO'
        user_status['is_admin'] = True
        return {'user_status': user_status}
    
    # Check Grievance student login
    if 'student_id' in session:
        user_status['is_logged_in'] = True
        user_status['is_guest'] = False
        user_status['user_name'] = session.get('student_name')
        user_status['user_module'] = 'Grievance'
        user_status['is_admin'] = False
        return {'user_status': user_status}
    
    # Check Grievance admin login
    if 'admin_id' in session and session.get('admin_id'):
        user_status['is_logged_in'] = True
        user_status['is_guest'] = False
        user_status['user_name'] = session.get('admin_name')
        user_status['user_module'] = 'Grievance'
        user_status['is_admin'] = True
        return {'user_status': user_status}
    
    return {'user_status': user_status}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============================================================================
# USER LOADER FOR FLASK-LOGIN
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login - tries multiple databases"""
    try:
        # Try LostLink users first
        from blueprints.lostlink_bp import Register
        user = Register.query.get(int(user_id))
        if user:
            return user
    except:
        pass
    
    try:
        # Try RGO users
        from blueprints.rgo_bp import User as RGOUser
        user = RGOUser.query.get(int(user_id))
        if user:
            return user
    except:
        pass
    
    return None

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BSU LIPA SMART KIOSK - UNIFIED SYSTEM")
    print("="*70)
    print("[INFO] Starting unified application on http://localhost:5000")
    print("[INFO] Available routes:")
    print("  - Dashboard:  http://localhost:5000/")
    print("  - Calendar:   http://localhost:5000/calendar")
    print("  - 3D Map:     http://localhost:5000/map")
    print("  - LostLink:   http://localhost:5000/lostlink/app")
    print("  - RGO:        http://localhost:5000/rgo/app")
    print("  - Grievance:  http://localhost:5000/grievance/app")
    print("="*70 + "\n")
    
    # Create all database tables
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database tables created/verified")
            
            # Initialize default admin accounts for RGO and LostLink
            from blueprints.rgo_bp import RGOAdmin
            from blueprints.lostlink_bp import LostLinkAdmin
            
            # Create default RGO admin if it doesn't exist
            rgo_admin = RGOAdmin.query.filter_by(username='admin').first()
            if not rgo_admin:
                rgo_admin = RGOAdmin(
                    username='admin',
                    email='admin@rgo.local',
                    full_name='System Administrator'
                )
                rgo_admin.set_password('admin123')
                db.session.add(rgo_admin)
                db.session.commit()
                print("[OK] RGO default admin account created (username: admin, password: admin123)")
            else:
                print("[INFO] RGO admin account already exists")
            
            # Create default LostLink admin if it doesn't exist
            lostlink_admin = LostLinkAdmin.query.filter_by(username='admin').first()
            if not lostlink_admin:
                lostlink_admin = LostLinkAdmin(
                    username='admin',
                    email='admin@lostlink.local',
                    full_name='System Administrator'
                )
                lostlink_admin.set_password('admin123')
                db.session.add(lostlink_admin)
                db.session.commit()
                print("[OK] LostLink default admin account created (username: admin, password: admin123)")
            else:
                print("[INFO] LostLink admin account already exists")
            
            print()
        except Exception as e:
            print(f"[!] Database initialization warning: {e}\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
