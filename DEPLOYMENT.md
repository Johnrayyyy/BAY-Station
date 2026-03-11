# BSU Kiosk System - Deployment Checklist

## Pre-Deployment Setup

### 1. Database Setup ✓
- [ ] PostgreSQL 13+ installed
- [ ] MySQL 8.0+ installed
- [ ] Run `python setup_databases.py` to create all databases
- [ ] Verify databases created:
  - PostgreSQL: `LostLink`, `grievance_system`
  - MySQL: `rgo_system`

### 2. Environment Configuration ✓
- [ ] Copy `.env.example` to `.env`
- [ ] Update database credentials in `.env`:
  ```
  LOSTLINK_DB_USER=your_postgres_user
  LOSTLINK_DB_PASSWORD=your_postgres_password
  RGO_DB_USER=root
  RGO_DB_PASSWORD=your_mysql_password
  ```
- [ ] Configure email settings for LostLink notifications
- [ ] Set secure SECRET_KEY (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)

### 3. Dependencies Installation ✓
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - Linux/Mac: `source venv/bin/activate`
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Verify installations: `pip list`

### 4. Database Tables Creation ✓
- [ ] Run the application once to auto-create tables: `python app.py`
- [ ] Verify tables in each database:
  - LostLink: users, reports, returns
  - RGO: users, products, orders, order_items, payments
  - Grievance: (auto-created by migrations)
- [ ] Create initial admin accounts for each module

### 5. Static Files & Uploads ✓
- [ ] Create uploads directory: `mkdir uploads`
- [ ] Set proper permissions on uploads folder
- [ ] Verify static files are accessible

### 6. Testing ✓
- [ ] Test dashboard loads at http://localhost:5000
- [ ] Test LostLink module:
  - [ ] User registration
  - [ ] Login/logout
  - [ ] Report lost item with file upload
  - [ ] Admin dashboard
- [ ] Test RGO module:
  - [ ] User registration
  - [ ] Browse products
  - [ ] Place order
  - [ ] Payment processing
- [ ] Test Grievance module:
  - [ ] Submit concern
  - [ ] Track concern status
  - [ ] Admin review

## Production Deployment

### 1. Security Hardening
- [ ] Change DEBUG to False in config.py
- [ ] Use strong SECRET_KEY (never use default)
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up database user with limited privileges (not root/postgres)
- [ ] Configure CORS properly for API endpoints
- [ ] Implement rate limiting
- [ ] Add CSRF protection

### 2. Server Configuration
- [ ] Choose deployment method:
  - [ ] Option A: Gunicorn + Nginx
  - [ ] Option B: Waitress (Windows)
  - [ ] Option C: Apache + mod_wsgi
- [ ] Configure reverse proxy
- [ ] Set up process manager (systemd, supervisor, pm2)
- [ ] Configure firewall rules

### 3. Performance Optimization
- [ ] Enable database connection pooling
- [ ] Configure caching (Redis/Memcached)
- [ ] Optimize static file serving
- [ ] Enable gzip compression
- [ ] Set up CDN for static assets (optional)

### 4. Monitoring & Logging
- [ ] Configure application logging
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Monitor database performance
- [ ] Set up uptime monitoring
- [ ] Configure backup automation

### 5. Backup Strategy
- [ ] Database backup schedule:
  - [ ] Daily automated backups
  - [ ] Weekly full backups
  - [ ] Monthly archives
- [ ] Uploaded files backup
- [ ] Configuration files backup
- [ ] Disaster recovery plan documented

## Post-Deployment

### 1. Launch Checklist
- [ ] Smoke test all critical features
- [ ] Verify email notifications working
- [ ] Test file uploads
- [ ] Check database connections
- [ ] Verify logging is working
- [ ] Test error pages (404, 500)

### 2. User Training
- [ ] Prepare user documentation
- [ ] Train administrative staff
- [ ] Create video tutorials (optional)
- [ ] Set up support channels

### 3. Maintenance Plan
- [ ] Schedule regular updates
- [ ] Monitor security advisories
- [ ] Plan database maintenance windows
- [ ] Document troubleshooting procedures

## Quick Commands Reference

```bash
# Development
python app.py                    # Start development server
python setup_databases.py        # Setup databases

# Production (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Database Management
# PostgreSQL
psql -U postgres -d LostLink
psql -U postgres -d grievance_system

# MySQL
mysql -u root -p rgo_system

# Backup Databases
pg_dump -U postgres LostLink > lostlink_backup.sql
pg_dump -U postgres grievance_system > grievance_backup.sql
mysqldump -u root -p rgo_system > rgo_backup.sql

# Restore Databases
psql -U postgres LostLink < lostlink_backup.sql
psql -U postgres grievance_system < grievance_backup.sql
mysql -u root -p rgo_system < rgo_backup.sql
```

## Troubleshooting Common Issues

### Database Connection Failed
1. Verify database server is running
2. Check credentials in .env file
3. Ensure database exists
4. Check firewall/network connectivity

### File Upload Issues
1. Check uploads directory exists and has write permissions
2. Verify MAX_CONTENT_LENGTH setting
3. Check disk space

### Module Not Loading
1. Verify blueprint is registered in app.py
2. Check route definitions
3. Review application logs

### Email Not Sending
1. Verify SMTP credentials
2. Check Gmail "Less secure apps" or use App Password
3. Test SMTP connection separately

## Support & Documentation

- Full documentation: `README.md`
- Quick start guide: `QUICKSTART.md`
- API documentation: `docs/API_DOCS.md`
- Configuration reference: `config.py`

---

**Last Updated:** 2024
**Version:** 1.0.0
