"""
RGO Blueprint - Records and Grade Office System
Integrated for BSU Kiosk System
Database: SQLite - databases/rgo.db
"""

from flask import Blueprint, render_template as flask_render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
from decimal import Decimal
from jinja2 import TemplateNotFound
import os


def render_template(template_name, **context):
    """Render RGO templates with a safe fallback to the module landing page."""
    try:
        return flask_render_template(template_name, **context)
    except TemplateNotFound:
        fallback_context = {'title': context.get('title', 'RGO Module')}
        return flask_render_template('module_rgo.html', **fallback_context)

# Create blueprint
rgo_bp = Blueprint('rgo', __name__,
                   template_folder='../templates/rgo',
                   static_folder='../static')

from extension import db

# ============================================================================
# MODELS
# ============================================================================

class User(db.Model):
    """User model – students, staff, and admins."""
    __bind_key__ = 'rgo'
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, staff, admin
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Product(db.Model):
    """Product model – items sold by RGO."""
    __bind_key__ = 'rgo'
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    image_path = db.Column(db.String(255), nullable=True)
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    """Order model – purchase orders by students."""
    __bind_key__ = 'rgo'
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.String(50), nullable=False, default='Pending')  # Pending, Approved, Paid, Ready for Pickup, Completed, Rejected
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='order', uselist=False, cascade='all, delete-orphan')

class OrderItem(db.Model):
    """Individual line items within an order."""
    __bind_key__ = 'rgo'
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

class Payment(db.Model):
    """Payment records for orders."""
    __bind_key__ = 'rgo'
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default='Cash')  # Cash, GCash
    payment_status = db.Column(db.String(50), nullable=False, default='Unpaid')  # Unpaid, Paid
    paid_at = db.Column(db.DateTime, nullable=True)

class RGOAdmin(db.Model):
    """RGO Admin model for authentication and management"""
    __bind_key__ = 'rgo'
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def role_required(*roles):
    """Decorator to restrict routes to specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first to continue.', 'warning')
                return redirect(url_for('rgo.login', next=request.path))
            if current_user.role not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('rgo.home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_order_reference(order):
    """Create a readable order reference number for students."""
    order_date = order.created_at.strftime('%Y%m%d') if order.created_at else datetime.utcnow().strftime('%Y%m%d')
    return f'RGO-{order_date}-{order.id:06d}'

def get_rgo_stats():
    """Get statistics for dashboard"""
    try:
        orders_count = Order.query.count()
        products_count = Product.query.filter_by(is_archived=False).count()
        users_count = User.query.count()
        return {
            'orders': orders_count,
            'products': products_count,
            'users': users_count
        }
    except:
        return {'orders': 0, 'products': 0, 'users': 0}

# ============================================================================
# ROUTES
# ============================================================================

@rgo_bp.route('/app')
@rgo_bp.route('/app/')
def home():
    """RGO home page"""
    try:
        available = Product.query.filter_by(is_archived=False).filter(Product.stock_quantity > 0).all()
        out_of_stock = Product.query.filter_by(is_archived=False, stock_quantity=0).all()
        return render_template('rgo/home.html', available=available, out_of_stock=out_of_stock, title='RGO System')
    except:
        return render_template('rgo/home.html', available=[], out_of_stock=[], title='RGO System')

@rgo_bp.route('/app/products')
def products():
    """Browse all products"""
    try:
        all_products = Product.query.filter_by(is_archived=False).order_by(Product.name).all()
        return render_template('rgo/products.html', products=all_products, title='Products')
    except:
        return render_template('rgo/products.html', products=[], title='Products')

@rgo_bp.route('/app/login', methods=['GET', 'POST'])
def login():
    """User login"""
    next_url = request.args.get('next', '').strip()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        next_url = request.form.get('next', '').strip() or request.args.get('next', '').strip()

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('rgo/login.html', title='Login', next_url=next_url, email=email)

        user = User.query.filter_by(email=email).first()
        if user:
            # Simple password check (in production, use proper hashing)
            from bcrypt import checkpw
            try:
                if checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                    login_user(user)
                    flash(f'Welcome back, {user.name}!', 'success')
                    # Only allow relative paths for post-login redirects.
                    if next_url and next_url.startswith('/'):
                        return redirect(next_url)
                    if user.role in ('staff', 'admin'):
                        return redirect(url_for('rgo.dashboard'))
                    return redirect(url_for('rgo.home'))
                else:
                    flash('Invalid email or password.', 'danger')
            except:
                flash('Invalid email or password.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')

        return render_template('rgo/login.html', title='Login', next_url=next_url, email=email)

    return render_template('rgo/login.html', title='Login', next_url=next_url, email='')

@rgo_bp.route('/app/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('rgo.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        student_id = request.form.get('student_id', '').strip() or None
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.query.filter_by(email=email).first():
            errors.append('Email is already registered.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('rgo/register.html', title='Register', 
                                 name=name, student_id=student_id, email=email)

        try:
            from bcrypt import hashpw, gensalt
            hashed = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
            user = User(name=name, student_id=student_id, email=email,
                         password_hash=hashed, role='student')
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in with your credentials.', 'success')
            return redirect(url_for('rgo.login', _external=False))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed. Please try again.', 'danger')
            return render_template('rgo/register.html', title='Register',
                                 name=name, student_id=student_id, email=email)

    return render_template('rgo/register.html', title='Register')

@rgo_bp.route('/app/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('rgo.home'))

@rgo_bp.route('/app/dashboard')
@role_required('staff', 'admin')
def dashboard():
    """Admin/Staff dashboard"""
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    products = Product.query.filter_by(is_archived=False).all()
    return render_template('rgo/dashboard.html', orders=orders, products=products, title='Dashboard')

@rgo_bp.route('/app/order/<int:product_id>', methods=['GET', 'POST'])
@role_required('student')
def order_product(product_id):
    """Student places order"""
    product = Product.query.get_or_404(product_id)

    if product.is_archived or product.stock_quantity <= 0:
        flash('This product is currently unavailable.', 'danger')
        return redirect(url_for('rgo.home'))

    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity', 1))
            payment_method = request.form.get('payment_method', 'Cash')

            if quantity < 1:
                flash('Quantity must be at least 1.', 'danger')
                return render_template('rgo/order_form.html', product=product, title='Place Order')

            if quantity > product.stock_quantity:
                flash(f'Only {product.stock_quantity} item(s) available.', 'danger')
                return render_template('rgo/order_form.html', product=product, title='Place Order')

            subtotal = Decimal(str(product.price)) * quantity

            # Create order
            order = Order(user_id=current_user.id, total_amount=subtotal, status='Pending')
            db.session.add(order)
            db.session.flush()

            item = OrderItem(order_id=order.id, product_id=product.id,
                             quantity=quantity, subtotal=subtotal)
            db.session.add(item)

            payment = Payment(order_id=order.id, payment_method=payment_method,
                              payment_status='Unpaid')
            db.session.add(payment)

            product.stock_quantity -= quantity
            db.session.commit()

            reference_no = generate_order_reference(order)
            # Redirect to order confirmation page instead of my_orders
            return redirect(url_for('rgo.order_confirmation', order_id=order.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error placing order: {str(e)}', 'danger')

    return render_template('rgo/order_form.html', product=product, title='Place Order')

@rgo_bp.route('/app/my-orders')
@role_required('student')
def my_orders():
    """View user's orders"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('rgo/my_orders.html', orders=orders, title='My Orders')

@rgo_bp.route('/app/order-confirmation/<int:order_id>')
@role_required('student')
def order_confirmation(order_id):
    """Display order confirmation with reference number"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure user can only view their own order confirmation
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('rgo.my_orders'))
    
    # Get order items to display product details
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    if order_items:
        item = order_items[0]  # Get first item
        product = Product.query.get(item.product_id)
        quantity = item.quantity
    else:
        product = None
        quantity = 0
    
    # Get payment method
    payment = Payment.query.filter_by(order_id=order.id).first()
    payment_method = payment.payment_method if payment else 'N/A'
    
    # Generate reference number
    reference_no = generate_order_reference(order)
    
    return render_template('rgo/order_confirmation.html', 
                          order=order, 
                          product=product, 
                          quantity=quantity,
                          payment_method=payment_method,
                          reference_no=reference_no, 
                          title='Order Confirmation')

@rgo_bp.route('/app/admin/orders')
@role_required('admin', 'staff')
def app_admin_orders():
    """Admin view all orders with filtering (old route)"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()
    
    stats = {
        'total': Order.query.count(),
        'pending': Order.query.filter_by(status='Pending').count(),
        'approved': Order.query.filter_by(status='Approved').count(),
        'paid': Order.query.filter_by(status='Paid').count(),
        'ready': Order.query.filter_by(status='Ready for Pickup').count(),
        'completed': Order.query.filter_by(status='Completed').count(),
        'rejected': Order.query.filter_by(status='Rejected').count(),
    }
    
    return render_template('rgo/admin_orders.html', orders=orders, stats=stats, 
                          current_status=status_filter, title='Order Management')

@rgo_bp.route('/app/admin/order/<int:order_id>/update', methods=['POST'])
@role_required('admin', 'staff')
def admin_update_order(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status', '')
    
    valid_statuses = ['Pending', 'Approved', 'Paid', 'Ready for Pickup', 'Completed', 'Rejected']
    if new_status not in valid_statuses:
        flash('Invalid status.', 'danger')
    else:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    
    return redirect(url_for('rgo.admin_orders'))

@rgo_bp.route('/app/admin/order/<int:order_id>/pay', methods=['POST'])
@role_required('admin', 'staff')
def admin_mark_paid(order_id):
    """Mark order as paid"""
    order = Order.query.get_or_404(order_id)
    
    if order.payment:
        order.payment.payment_status = 'Paid'
        order.payment.paid_at = datetime.utcnow()
        order.status = 'Approved'
        db.session.commit()
        flash(f'Order #{order.id} marked as paid.', 'success')
    else:
        flash('Payment record not found.', 'danger')
    
    return redirect(url_for('rgo.admin_orders'))

@rgo_bp.route('/app/admin/products')
@role_required('admin', 'staff')
def app_admin_products():
    """Admin manage products (old route)"""
    products = Product.query.all()
    return render_template('rgo/admin_products.html', products=products, title='Product Management')

@rgo_bp.route('/app/admin/product/add', methods=['GET', 'POST'])
@role_required('admin')
def app_admin_add_product():
    """Add new product"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', '0')
            stock_quantity = request.form.get('stock_quantity', '0')
            
            if not name or not price:
                flash('Product name and price are required.', 'danger')
                return render_template('rgo/add_product.html', title='Add Product')
            
            price = Decimal(price)
            stock_quantity = int(stock_quantity)
            
            # Handle image upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    # Secure the filename and save
                    filename = secure_filename(file.filename)
                    # Add timestamp to prevent overwriting
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    # Save to static/images/rgo folder
                    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'rgo')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    # Store relative path for database
                    image_path = f'images/rgo/{filename}'
            
            product = Product(name=name, description=description, price=price,
                            stock_quantity=stock_quantity, is_archived=False,
                            image_path=image_path)
            db.session.add(product)
            db.session.commit()
            
            flash(f'Product "{name}" added successfully!', 'success')
            return redirect(url_for('rgo.app_admin_products'))
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'danger')
            return render_template('rgo/add_product.html', title='Add Product')
    
    return render_template('rgo/add_product.html', title='Add Product')

@rgo_bp.route('/app/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
@role_required('admin')
def app_admin_edit_product(product_id):
    """Edit existing product"""
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', '').strip() or product.name
            product.description = request.form.get('description', '').strip()
            product.price = Decimal(request.form.get('price', product.price))
            product.stock_quantity = int(request.form.get('stock_quantity', product.stock_quantity))
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    # Delete old image if it exists
                    if product.image_path:
                        old_image = os.path.join(current_app.root_path, 'static', product.image_path)
                        if os.path.exists(old_image):
                            try:
                                os.remove(old_image)
                            except:
                                pass
                    
                    # Save new image
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'rgo')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    product.image_path = f'images/rgo/{filename}'
            
            db.session.commit()
            flash(f'Product "{product.name}" updated successfully!', 'success')
            return redirect(url_for('rgo.app_admin_products'))
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'danger')
    
    return render_template('rgo/edit_product.html', product=product, title='Edit Product')

@rgo_bp.route('/app/admin/product/<int:product_id>/archive', methods=['POST'])
@role_required('admin')
def app_admin_archive_product(product_id):
    """Archive a product"""
    product = Product.query.get_or_404(product_id)
    product.is_archived = not product.is_archived
    db.session.commit()
    
    status = 'archived' if product.is_archived else 'restored'
    flash(f'Product "{product.name}" has been {status}.', 'success')
    return redirect(url_for('rgo.admin_products'))

@rgo_bp.route('/app/admin/analytics')
@role_required('admin', 'staff')
def admin_analytics():
    """View system analytics"""
    try:
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.status.in_(['Paid', 'Completed'])
        ).scalar() or 0
        
        stats = {
            'total_orders': Order.query.count(),
            'total_revenue': float(total_revenue),
            'total_users': User.query.count(),
            'total_products': Product.query.filter_by(is_archived=False).count(),
            'low_stock_products': Product.query.filter(
                Product.stock_quantity < 5,
                Product.is_archived == False
            ).all(),
            'recent_orders': Order.query.order_by(Order.created_at.desc()).limit(10).all(),
        }
        
        return render_template('rgo/admin_analytics.html', stats=stats, title='Analytics')
    except:
        return render_template('rgo/admin_analytics.html', stats={}, title='Analytics')

# ============================================================================  
# ADMIN AUTHENTICATION & MANAGEMENT
# ============================================================================

@rgo_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = RGOAdmin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['rgo_admin_id'] = admin.id
            session['rgo_admin_name'] = admin.full_name
            flash(f'Welcome back, {admin.full_name}!', 'success')
            return redirect(url_for('rgo.admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('rgo/admin_login.html', title='Admin Login')

@rgo_bp.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if 'rgo_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('rgo.admin_login'))
    
    try:
        orders_count = Order.query.count()
        pending_orders = Order.query.filter_by(status='Pending').count()
        products_count = Product.query.filter_by(is_archived=False).count()
        users_count = User.query.count()
        
        stats = {
            'total_orders': orders_count,
            'pending_orders': pending_orders,
            'total_products': products_count,
            'total_users': users_count,
            'recent_orders': Order.query.order_by(Order.created_at.desc()).limit(10).all(),
            'low_stock': Product.query.filter(Product.stock_quantity < 5, Product.is_archived == False).all()
        }
        
        return render_template('rgo/admin_dashboard.html', stats=stats, admin_name=session.get('rgo_admin_name'), title='Admin Dashboard')
    except:
        return render_template('rgo/admin_dashboard.html', stats={}, admin_name=session.get('rgo_admin_name'), title='Admin Dashboard')

@rgo_bp.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('rgo_admin_id', None)
    session.pop('rgo_admin_name', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('rgo.admin_login'))

@rgo_bp.route('/admin/users')
def admin_users():
    """Manage users"""
    if 'rgo_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('rgo.admin_login'))
    
    users = User.query.all()
    return render_template('rgo/admin_users.html', users=users, admin_name=session.get('rgo_admin_name'), title='Manage Users')

@rgo_bp.route('/admin/user/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """Delete user"""
    if 'rgo_admin_id' not in session:
        return redirect(url_for('rgo.admin_login'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} deleted successfully', 'success')
    return redirect(url_for('rgo.admin_users'))

@rgo_bp.route('/admin/products')
def admin_products():
    """Manage products"""
    if 'rgo_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('rgo.admin_login'))
    
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('rgo/admin_products.html', products=products, admin_name=session.get('rgo_admin_name'), title='Manage Products')

@rgo_bp.route('/admin/product/add', methods=['GET', 'POST'])
def admin_add_product():
    """Add new product"""
    if 'rgo_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('rgo.admin_login'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', '0')
            stock_quantity = request.form.get('stock_quantity', '0')
            
            if not name or not price:
                flash('Product name and price are required.', 'danger')
                return render_template('rgo/admin_add_product.html', admin_name=session.get('rgo_admin_name'), title='Add Product')
            
            price = Decimal(price)
            stock_quantity = int(stock_quantity)
            
            # Handle image upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    # Secure the filename and save
                    filename = secure_filename(file.filename)
                    # Add timestamp to prevent overwriting
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    # Save to static/images/rgo folder
                    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'rgo')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    # Store relative path for database
                    image_path = f'images/rgo/{filename}'
            
            product = Product(name=name, description=description, price=price,
                            stock_quantity=stock_quantity, is_archived=False,
                            image_path=image_path)
            db.session.add(product)
            db.session.commit()
            
            flash(f'Product "{name}" added successfully!', 'success')
            return redirect(url_for('rgo.admin_products'))
        except Exception as e:
            flash(f'Error adding product: {str(e)}', 'danger')
    
    return render_template('rgo/admin_add_product.html', admin_name=session.get('rgo_admin_name'), title='Add Product')

@rgo_bp.route('/admin/product/<int:product_id>/edit', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    """Edit existing product"""
    if 'rgo_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('rgo.admin_login'))
    
    product = Product.query.get_or_404(product_id)
    
    if request.method == 'POST':
        try:
            product.name = request.form.get('name', '').strip() or product.name
            product.description = request.form.get('description', '').strip()
            product.price = Decimal(request.form.get('price', product.price))
            product.stock_quantity = int(request.form.get('stock_quantity', product.stock_quantity))
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    # Delete old image if it exists
                    if product.image_path:
                        old_image = os.path.join(current_app.root_path, 'static', product.image_path)
                        if os.path.exists(old_image):
                            try:
                                os.remove(old_image)
                            except:
                                pass
                    
                    # Save new image
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    upload_folder = os.path.join(current_app.root_path, 'static', 'images', 'rgo')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    product.image_path = f'images/rgo/{filename}'
            
            db.session.commit()
            flash(f'Product "{product.name}" updated successfully!', 'success')
            return redirect(url_for('rgo.admin_products'))
        except Exception as e:
            flash(f'Error updating product: {str(e)}', 'danger')
    
    return render_template('rgo/admin_edit_product.html', product=product, admin_name=session.get('rgo_admin_name'), title='Edit Product')

@rgo_bp.route('/admin/product/<int:product_id>/delete', methods=['POST'])
def admin_delete_product(product_id):
    """Delete product"""
    if 'rgo_admin_id' not in session:
        return redirect(url_for('rgo.admin_login'))
    
    product = Product.query.get_or_404(product_id)
    product_name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product_name}" deleted successfully', 'success')
    return redirect(url_for('rgo.admin_products'))

@rgo_bp.route('/admin/product/<int:product_id>/toggle-archive', methods=['POST'])
def admin_toggle_archive_product(product_id):
    """Archive/restore product"""
    if 'rgo_admin_id' not in session:
        return redirect(url_for('rgo.admin_login'))
    
    product = Product.query.get_or_404(product_id)
    product.is_archived = not product.is_archived
    db.session.commit()
    
    status = 'archived' if product.is_archived else 'restored'
    flash(f'Product "{product.name}" has been {status}.', 'success')
    return redirect(url_for('rgo.admin_products'))

@rgo_bp.route('/admin/orders')
def admin_orders():
    """Manage orders"""
    if 'rgo_admin_id' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('rgo.admin_login'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('rgo/admin_orders.html', orders=orders, admin_name=session.get('rgo_admin_name'), title='Manage Orders')

# Export for main app
__all__ = ['rgo_bp', 'User', 'Product', 'Order', 'OrderItem', 'Payment', 'RGOAdmin', 'get_rgo_stats']
