# BSU LIPA SMART KIOSK - UNIFIED SYSTEM

A complete integrated kiosk system for Batangas State University - Lipa Campus, consolidating three major modules into one unified Flask application.

## 📋 System Overview

The BSU Smart Kiosk integrates three essential campus services:

### 1. **LostLink** - Lost and Found Management
- Report lost items with photos and descriptions
- Browse found items
- Email notifications for matched items  
- Admin dashboard for managing reports
- Student and admin roles
- **Database**: PostgreSQL (`LostLink`)

### 2. **RGO** - Records & Grade Office
- Campus resource and merchandise sales
- Product catalog and ordering
- Payment tracking (Cash/GCash)
- Order management system
- Student, staff, and admin roles
- **Database**: MySQL (`rgo_system`)

### 3. **Grievance System** - Student Concerns
- Submit and track student grievances
- Concern categorization and status tracking
- Admin resolution workflows
- Email notifications
- **Database**: PostgreSQL (`grievance_system`)

## 🏗️ System Architecture

```
BSU_Kiosk_System/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── blueprints/            # Module blueprints
│   ├── lostlink_bp.py    # LostLink module
│   ├── rgo_bp.py         # RGO module
│   ├── grievance_bp.py   # Grievance frontend
│   └── grievance_api.py  # Grievance API
├── templates/             # HTML templates
│   ├── dashboard.html    # Main kiosk dashboard
│   ├── calendar.html     # Events calendar
│   ├── map.html          # 3D campus map
│   ├── lostlink/         # LostLink templates
│   ├── rgo/              # RGO templates
│   └── grievance/        # Grievance templates
├── static/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── uploads/          # User uploads
└── database/              # Database schemas
    ├── lostlink.sql      # LostLink schema
    ├── rgo.sql           # RGO schema
    └── grievance.sql     # Grievance schema
```

## 🔧 Prerequisites

### Software Requirements
- **Python 3.8+**
- **PostgreSQL 13+** (for LostLink and Grievance)
- **MySQL 8.0+** (for RGO)
- **Git** (optional, for version control)

### Python Packages
All packages listed in `requirements.txt`

## 📦 Installation Guide

### Step 1: Clone or Copy the System

```bash
# Navigate to your project directory
cd "c:\Users\johnr\OneDrive\Documents\Assignment_BSU\Info Management\Project\final last"

# The BSU_Kiosk_System folder is already created
cd BSU_Kiosk_System
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Database Setup

#### PostgreSQL Databases

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create LostLink database
CREATE DATABASE "LostLink";

-- Create Grievance database
CREATE DATABASE grievance_system;

-- Create users table for LostLink
\c LostLink;
CREATE TABLE users (
    sr_code VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL
);

-- Create reports table
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    item VARCHAR(255) NOT NULL,
    place VARCHAR(255) NOT NULL,
    photo VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    report_by VARCHAR(255) REFERENCES users(sr_code)
);

-- Create returns table
CREATE TABLE returns (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    place_found VARCHAR(255) NOT NULL,
    photo VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    claimed_by VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    contact VARCHAR(50) NOT NULL,
    timestamp_claimed TIMESTAMP DEFAULT NOW()
);
```

#### MySQL Database (RGO)

```sql
-- Connect to MySQL
mysql -u root-p

-- Create RGO database
CREATE DATABASE rgo_system;
USE rgo_system;

-- Create users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    student_id VARCHAR(20),
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'staff', 'admin') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    image_path VARCHAR(255),
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status ENUM('Pending', 'Approved', 'Paid', 'Ready for Pickup', 'Completed', 'Rejected') NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create order_items table
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Create payments table
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method ENUM('Cash', 'GCash') NOT NULL DEFAULT 'Cash',
    payment_status ENUM('Unpaid', 'Paid') NOT NULL DEFAULT 'Unpaid',
    paid_at TIMESTAMP NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
```

### Step 5: Configure Database Credentials

Edit `config.py` or create a `.env` file:

```env
# LostLink Database (PostgreSQL)
LOSTLINK_DB_USER=postgres
LOSTLINK_DB_PASSWORD=johnray08
LOSTLINK_DB_NAME=LostLink

# RGO Database (MySQL)
RGO_DB_USER=root
RGO_DB_PASSWORD=your_mysql_password
RGO_DB_NAME=rgo_system

# Grievance Database (PostgreSQL)
GRIEVANCE_DB_USER=postgres
GRIEVANCE_DB_PASSWORD=your_postgres_password
GRIEVANCE_DB_NAME=grievance_system

# Email Configuration
MAIL_USERNAME=lostlink.official@gmail.com
MAIL_PASSWORD=izhu jksj gqfs ilcj
```

### Step 6: Initialize the Application

```powershell
# Run the application
python app.py
```

The system will:
- Initialize all databases
- Create necessary tables
- Start the Flask development server on port 5000

## 🚀 Running the System

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Run the application
python app.py
```

Access the system at:
- **Main Dashboard**: http://localhost:5000/
- **Calendar**: http://localhost:5000/calendar
- **3D Map**: http://localhost:5000/map
- **LostLink**: http://localhost:5000/lostlink/app
- **RGO**: http://localhost:5000/rgo/app
- **Grievance**: http://localhost:5000/grievance/app

## 📱 Features

### Main Dashboard
- Unified statistics from all modules
- Real-time activity feed
- Quick access to all services
- Interactive charts and visualizations

### Calendar System
- Campus events calendar
- Event categorization (Academic, Social, Sports, Administrative)
- Add/Edit/Delete events
- FullCalendar integration

### 3D Campus Map
- Interactive 3D visualization of BSU Lipa campus
- Click buildings to navigate to respective modules
- Camera controls (rotate, zoom, pan)
- Building information tooltips

## 🔐 User Roles

### LostLink
- **Student**: Report lost items, browse found items
- **Admin**: Manage reports, process returns, send notifications

### RGO
- **Student**: Browse products, place orders
- **Staff**: Manage orders, update statuses
- **Admin**: Full system access, manage products and users

### Grievance
- **Student**: Submit concerns, track status
- **Admin**: Review and resolve grievances, manage users

## 🗄️ Database Configuration

### Connection Details

| Module | Database | Type | Port | Default User |
|--------|----------|------|------|--------------|
| LostLink | LostLink | PostgreSQL | 5432 | postgres |
| RGO | rgo_system | MySQL | 3306 | root |
| Grievance | grievance_system | PostgreSQL | 5432 | postgres |

### Database Binding

The system uses SQLAlchemy's `SQLALCHEMY_BINDS` feature to manage multiple databases:

```python
SQLALCHEMY_BINDS = {
    'lostlink': 'postgresql://postgres:password@localhost/LostLink',
    'rgo': 'mysql+pymysql://root:password@localhost/rgo_system',
    'grievance': 'postgresql://postgres:password@localhost/grievance_system'
}
```

Each model specifies its database using `__bind_key__`:

```python
class Register(db.Model):
    __bind_key__ = 'lostlink'
    # ... model definition
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**PostgreSQL Authentication Failed**
```
Solution: Update password in config.py or .env file
Check PostgreSQL is running: 
  Windows: Services → PostgreSQL
  Check connection: psql -U postgres
```

**MySQL Connection Error**
```
Solution: Ensure MySQL server is running
  Windows: Services → MySQL
  Test connection: mysql -u root -p
```

#### 2. Port 5000 Already in Use

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### 3. Module Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Upload Directory Errors

```powershell
# Create uploads directory manually
mkdir static\uploads
```

## 📊 API Endpoints

### Dashboard API
- `GET /api/stats` - Get system statistics
- `GET /api/activity-data` - Get monthly activity data
- `GET /api/module-usage` - Get module usage stats
- `GET /api/weekly-trends` - Get weekly trend data
- `GET /api/activities` - Get recent activities

### Calendar API
- `GET /api/events` - Get all events
- `POST /api/events` - Create new event
- `DELETE /api/events/<id>` - Delete event

### Grievance API
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/concerns` - Get all concerns
- `POST /api/concerns` - Create concern
- `GET /api/concerns/<id>` - Get specific concern
- `PUT /api/concerns/<id>` - Update concern
- `DELETE /api/concerns/<id>` - Delete concern

## 🔄 System Workflow

### LostLink Flow
1. Student reports lost item → Stored in database
2. Admin views reports → Marks as found when item recovered
3. System sends email notification to item owner
4. Item moved to "Returned" database table

### RGO Flow
1. Student browses products → Selects item and quantity
2. System creates order → Deducts from stock
3. Payment recorded (Cash/GCash)
4. Staff updates order status → Student notified
5. Order marked as completed when picked up

### Grievance Flow
1. Student submits concern → Assigned tracking number
2. Admin reviews concern → Updates status
3. Resolution notes added → Student can view updates
4. Concern marked as resolved → Archived

## 📝 Development Notes

### Adding New Features

1. Create new route in appropriate blueprint
2. Add corresponding template
3. Update navigation menus
4. Test database connectivity
5. Document new endpoint/feature

### Database Migrations

For production, consider using Flask-Migrate:

```powershell
pip install Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🤝 Contributing

This system was developed for BSU Lipa. To contribute:

1. Test thoroughly in development environment
2. Document all changes
3. Follow existing code structure
4. Update this README with new features

## 📄 License

This project is developed for academic purposes at Batangas State University - Lipa Campus.

## 👥 Credits

**Development Team**: Group 9
- LostLink Module
- RGO Module
- Grievance Module
- System Integration

**Institution**: Batangas State University - Lipa Campus
**Course**: Information Management
**Year**: 2026

## 📞 Support

For issues or questions:
- Check this README first
- Review error messages in terminal
- Verify database connections
- Check Python and database versions

---

**Last Updated**: March 6, 2026  
**Version**: 1.0.0  
**Status**: Production Ready ✅
