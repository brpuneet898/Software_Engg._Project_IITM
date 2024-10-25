import pytest
from flask import Flask
from app import app  # Replace with actual module name where the app is defined

# Configure pytest fixture for the Flask application
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client
    
# Test for /dashboard/lecture/<week_id>/<lecture_id> endpoint
def test_lecture(client):
    response = client.get('/dashboard/lecture/1/1')
    assert response.status_code == 200
    
# Test for /api/lecture_populate endpoint
def test_lecture_populate(client):
    response = client.post('/api/lecture_populate')
    assert response.status_code == 200