"""
Test Suite for BSU Kiosk System
Run with: pytest test_system.py -v
"""

import pytest
from app import app, db
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def client():
    """Create test client"""
    app.config.from_object(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

class TestMainRoutes:
    """Test main application routes"""
    
    def test_dashboard_loads(self, client):
        """Test dashboard page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_calendar_loads(self, client):
        """Test calendar page loads"""
        response = client.get('/calendar')
        assert response.status_code == 200
        assert b'Academic Calendar' in response.data
    
    def test_map_loads(self, client):
        """Test map page loads"""
        response = client.get('/map')
        assert response.status_code == 200
        assert b'Campus Map' in response.data
    
    def test_404_page(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_stats_api(self, client):
        """Test statistics API endpoint"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'lost_items' in data
        assert 'rgo_requests' in data
        assert 'grievances' in data
        assert 'total_users' in data
    
    def test_activity_data_api(self, client):
        """Test activity data API endpoint"""
        response = client.get('/api/activity-data')
        assert response.status_code == 200
        data = response.get_json()
        assert 'labels' in data
        assert 'datasets' in data

class TestLostLinkModule:
    """Test LostLink module"""
    
    def test_lostlink_landing(self, client):
        """Test LostLink landing page"""
        response = client.get('/lostlink')
        assert response.status_code == 200
        assert b'LostLink' in response.data
    
    def test_lostlink_login_page(self, client):
        """Test LostLink login page loads"""
        response = client.get('/lostlink/app/login')
        assert response.status_code == 200
    
    def test_lostlink_register_page(self, client):
        """Test LostLink register page loads"""
        response = client.get('/lostlink/app/register')
        assert response.status_code == 200

class TestRGOModule:
    """Test RGO module"""
    
    def test_rgo_landing(self, client):
        """Test RGO landing page"""
        response = client.get('/rgo')
        assert response.status_code == 200
        assert b'RGO' in response.data
    
    def test_rgo_login_page(self, client):
        """Test RGO login page loads"""
        response = client.get('/rgo/app/login')
        assert response.status_code == 200
    
    def test_rgo_register_page(self, client):
        """Test RGO register page loads"""
        response = client.get('/rgo/app/register')
        assert response.status_code == 200

class TestGrievanceModule:
    """Test Grievance module"""
    
    def test_grievance_landing(self, client):
        """Test Grievance landing page"""
        response = client.get('/grievance')
        assert response.status_code == 200
        assert b'Grievance' in response.data
    
    def test_grievance_login_page(self, client):
        """Test Grievance login page loads"""
        response = client.get('/grievance/app/login')
        assert response.status_code == 200

class TestDatabaseModels:
    """Test database models"""
    
    def test_lostlink_models(self):
        """Test LostLink models are defined"""
        from blueprints.lostlink_bp import Register, Report, Return
        assert Register.__tablename__ == 'users'
        assert Report.__tablename__ == 'reports'
        assert Return.__tablename__ == 'returns'
    
    def test_rgo_models(self):
        """Test RGO models are defined"""
        from blueprints.rgo_bp import User, Product, Order, OrderItem, Payment
        assert User.__tablename__ == 'users'
        assert Product.__tablename__ == 'products'
        assert Order.__tablename__ == 'orders'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
