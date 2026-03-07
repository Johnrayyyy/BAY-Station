# BSU KIOSK SYSTEM - QUICK START GUIDE

## 🚀 Quick Setup (5 Minutes)

### 1. Install Requirements
```powershell
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup Databases

**PostgreSQL (LostLink & Grievance)**
```sql
psql -U postgres
CREATE DATABASE "LostLink";
CREATE DATABASE grievance_system;
```

**MySQL (RGO)**
```sql
mysql -u root -p
CREATE DATABASE rgo_system;
```

### 3. Configure Settings

Copy `.env.example` to `.env` and update passwords:
```
LOSTLINK_DB_PASSWORD=your_password
RGO_DB_PASSWORD=your_password
GRIEVANCE_DB_PASSWORD=your_password
```

### 4. Run Application

```powershell
python app.py
```

### 5. Access System

Open browser: http://localhost:5000

## 📍 URLs

- Dashboard: http://localhost:5000/
- LostLink: http://localhost:5000/lostlink/app
- RGO: http://localhost:5000/rgo/app
- Grievance: http://localhost:5000/grievance/app
- Calendar: http://localhost:5000/calendar
- 3D Map: http://localhost:5000/map

## ⚡ Common Commands

```powershell
# Start server
python app.py

# Install new package
pip install package_name
pip freeze > requirements.txt

# Database shell
psql -U postgres -d LostLink  # PostgreSQL
mysql -u root -p rgo_system   # MySQL

# Virtual environment
.\venv\Scripts\activate   # Activate
deactivate                # Deactivate
```

## 🐛 Quick Fixes

**Port in use?**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Database error?**
- Check services are running
- Verify credentials in .env
- Ensure databases exist

**Import error?**
```powershell
pip install -r requirements.txt --force-reinstall
```

## 📚 Need More Help?

See full README.md for detailed instructions.
