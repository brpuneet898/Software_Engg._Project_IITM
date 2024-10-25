import pytest
from flask import Flask
from app import app  # Replace with actual module name where the app is defined

# Configure pytest fixture for the Flask application
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client

# Test for /analyze endpoint
def test_submission_analysis(client):
    data = {
        "week": "1",
        "question-1": "A",
        "question-2": "B"
    }
    response = client.post('/analyze', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "Software Development" in json_data

# Test for /analyze_doubt endpoint
def test_analyze_doubt(client):
    data = {
        "week": "1",
        "question_index": "1",
        "doubt": "What are components in software engineering?"
    }
    response = client.post('/analyze_doubt', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "components" in json_data

# Test for /dashboard/gradedassignment/<week_id> endpoint
def test_gradedassignment(client):
    response = client.get('/dashboard/gradedassignment/1')
    assert response.status_code == 200

# Test for /submit endpoint
def test_temp_submission(client):
    data = {
        "week": "1",
        "question-1": "A",
        "question-2": "B"
    }
    response = client.post('/submit', data=data)
    assert response.status_code == 200

# Test for /api/complete_assignment_feedback endpoint
def test_complete_assignment_feedback(client):
    data = [
        ["What is Flask?", ["A web framework", "A type of container"], "A web framework", "A web framework"]
    ]
    response = client.post('/api/complete_assignment_feedback', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "response" in json_data

# Test for /api/process_regular_questions endpoint
def test_process_regular_questions(client):
    data = {
        "question": "What is Flask?",
        "options": ["A web framework", "A type of container"]
    }
    response = client.post('/api/process_regular_questions', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "response" in json_data

# Test for /api/populate_assignments endpoint
def test_populate_assignments(client):
    response = client.post('/api/populate_assignments')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data.get("message") == "Success"

# Test for /api/gradedassignment/<week_id>/clear endpoint
def test_gradedassignmentreset(client):
    response = client.get('/api/gradedassignment/1/clear')
    assert response.status_code == 200

  