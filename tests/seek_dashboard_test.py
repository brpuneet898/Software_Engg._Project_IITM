import pytest
from flask import Flask
from app import app  # Replace with actual module name where the app is defined

# Configure pytest fixture for the Flask application
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client

# Test for /api/logout endpoint
def test_logout_user(client):
    response = client.delete('/api/logout')
    assert response.status_code == 200


# Test for / endpoint
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    
# Test for /dashboard endpoint
def test_dashboard(client):
    response = client.get('/dashboard')
    assert response.status_code == 200

# Test for /dashboard/chatbot endpoint
def test_chatbot(client):
    response = client.get('/dashboard/chatbot')
    assert response.status_code == 200