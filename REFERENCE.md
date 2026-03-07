# BSU Kiosk System - Quick Reference Guide

## 🚀 Getting Started in 3 Steps

```bash
# 1. Setup databases
python setup_databases.py

# 2. Configure environment
cp .env.example .env
# Edit .env with your database passwords

# 3. Run the application
pip install -r requirements.txt
python app.py
```

Visit: **http://localhost:5000**

---

## 📁 Project Structure

```
BSU_Kiosk_System/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── setup_databases.py     # Database setup wizard
├── .env                   # Environment variables (create from .env.example)
│
├── blueprints/           # Module blueprints
│   ├── lostlink_bp.py   # Lost & Found module
│   ├── rgo_bp.py        # Records & Grade Office module
│   ├── grievance_bp.py  # Grievance system frontend
│   └── grievance_api.py # Grievance API endpoints
│
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── dashboard.html   # Main dashboard
│   ├── calendar.html    # Academic calendar
│   ├── map.html         # Campus map
│   ├── module_*.html    # Module landing pages
│   └── 404.html         # Error page
│
└── uploads/              # User uploaded files
```

---

## 🔧 Configuration Quick Reference

### Database Connections (.env)
```bash
# PostgreSQL - LostLink
LOSTLINK_DB_HOST=localhost
LOSTLINK_DB_USER=postgres
LOSTLINK_DB_PASSWORD=your_password
LOSTLINK_DB_NAME=LostLink

# MySQL - RGO
RGO_DB_HOST=localhost
RGO_DB_USER=root
RGO_DB_PASSWORD=your_password
RGO_DB_NAME=rgo_system

# PostgreSQL - Grievance
GRIEVANCE_DB_HOST=localhost
GRIEVANCE_DB_USER=postgres
GRIEVANCE_DB_PASSWORD=your_password
GRIEVANCE_DB_NAME=grievance_system

# Email (LostLink notifications)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### Flask Settings
```python
DEBUG = True              # Set to False in production
PORT = 5000              # Application port
SECRET_KEY = 'generate-secure-key'  # Use secrets.token_hex(32)
```

---

## 🌐 URL Routes

### Main System
- **Dashboard:** `http://localhost:5000/`
- **Calendar:** `http://localhost:5000/calendar`
- **Campus Map:** `http://localhost:5000/map`

### LostLink Module (Lost & Found)
- **Landing:** `http://localhost:5000/lostlink`
- **Login:** `http://localhost:5000/lostlink/app/login`
- **Register:** `http://localhost:5000/lostlink/app/register`
- **Dashboard:** `http://localhost:5000/lostlink/app/dashboard`
- **Report Lost Item:** `http://localhost:5000/lostlink/app/report`
- **Admin Panel:** `http://localhost:5000/lostlink/app/admin`

### RGO Module (Records & Grade Office)
- **Landing:** `http://localhost:5000/rgo`
- **Login:** `http://localhost:5000/rgo/app/login`
- **Register:** `http://localhost:5000/rgo/app/register`
- **Dashboard:** `http://localhost:5000/rgo/app/dashboard`
- **Products:** `http://localhost:5000/rgo/app/products`
- **My Orders:** `http://localhost:5000/rgo/app/orders`

### Grievance Module
- **Landing:** `http://localhost:5000/grievance`
- **Login:** `http://localhost:5000/grievance/app/login`
- **Register:** `http://localhost:5000/grievance/app/register`
- **Student Dashboard:** `http://localhost:5000/grievance/app/student-dashboard`
- **Admin Dashboard:** `http://localhost:5000/grievance/app/admin-dashboard`

### API Endpoints
- **Dashboard Stats:** `GET /api/stats`
- **Activity Data:** `GET /api/activity-data`
- **Grievance API:** `/api/*` (see grievance_api.py)

---

## 💾 Database Commands

### PostgreSQL
```bash
# Connect to databases
psql -U postgres -d LostLink
psql -U postgres -d grievance_system

# List tables
\dt

# Backup
pg_dump -U postgres LostLink > backup.sql

# Restore
psql -U postgres LostLink < backup.sql
```

### MySQL
```bash
# Connect to database
mysql -u root -p rgo_system

# Show tables
SHOW TABLES;

# Backup
mysqldump -u root -p rgo_system > backup.sql

# Restore
mysql -u root -p rgo_system < backup.sql
```

---

## 📦 Module Features

### LostLink (Lost & Found)
✓ Report lost items with photos  
✓ Search found items  
✓ Email notifications  
✓ Admin dashboard  
✓ Claim management  

### RGO (Records & Grade Office)
✓ Student registration  
✓ Campus store products  
✓ Order processing  
✓ Payment tracking (Cash/GCash)  
✓ Order history  

### Grievance System
✓ Submit concerns/complaints  
✓ Track concern status  
✓ Admin review system  
✓ Priority management  
✓ Response tracking  

---

## 🔐 User Roles

Each module has its own user authentication:

| Module | Roles |
|--------|-------|
| LostLink | Student, Admin |
| RGO | Student, Staff, Admin |
| Grievance | Student, Admin, Super Admin |

---

## 🛠️ Common Tasks

### Create Admin User (LostLink)
```python
from blueprints.lostlink_bp import Register
from werkzeug.security import generate_password_hash
# Use your database tool to insert admin user
```

### Clear Uploaded Files
```bash
# Windows
del /Q uploads\*
# Linux/Mac
rm -f uploads/*
```

### Reset Database
```bash
# Drop and recreate databases
python setup_databases.py
python app.py  # Auto-creates tables
```

### Check Logs
```python
# Add to app.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use different port
```

### Database Connection Error
1. Verify database servers are running
2. Check credentials in .env file
3. Ensure databases exist (run setup_databases.py)

### Module Import Error
```bash
# Make sure you're in the correct directory
cd BSU_Kiosk_System
python app.py
```

### Template Not Found
- Verify template file exists in templates/ folder
- Check blueprint template_folder configuration

---

## 📊 Dashboard Statistics

The main dashboard displays:
- **Lost Items Count:** From LostLink database
- **RGO Requests:** From RGO orders
- **Grievances:** From Grievance concerns
- **Total Users:** Combined from all modules

Data is fetched via `/api/stats` endpoint.

---

## 🔄 Update & Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Backup Before Updates
```bash
# Backup databases (see Database Commands above)
# Backup uploaded files
cp -r uploads/ uploads_backup/
```

### Version Control
```bash
git init
git add .
git commit -m "Initial commit"
```

---

## 📚 Additional Resources

- **Full Documentation:** [README.md](README.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)

---

## 🆘 Getting Help

If you encounter issues:
1. Check error messages in terminal
2. Review logs in browser console (F12)
3. Verify database connections
4. Ensure all dependencies installed
5. Check file permissions for uploads/

---

**System Version:** 1.0.0  
**Python Required:** 3.8+  
**Last Updated:** 2024
