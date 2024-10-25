import pytest
from flask import Flask
from app import app  # Replace with actual module name where the app is defined

# Configure pytest fixture for the Flask application
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client

# Test for /api/chatbot_page endpoint
def test_chatbot_page(client):
    response = client.post('/api/chatbot_page', json={'message': 'Hello chatbot!'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'response' in data
    assert isinstance(data['response'], str)

# Test for /api/chat/clear endpoint
def test_clearchat(client):
    response = client.get('/api/chat/clear')
    assert response.status_code == 200
    assert response.get_json() == {"message":"chat cleared"}


# Test for /api/chat_chain endpoint
def test_chat_chain(client):
    conversation_chain = {
        "messages": [
            {"role": "user", "content": "What is the weather?"},
            {"role": "assistant", "content": "It's sunny today."},
            {"role": "user", "content": "Will it rain tomorrow?"}
        ]
    }
    response = client.post('/api/chat_chain', json=conversation_chain)
    assert response.status_code == 200
    data = response.get_json()
    assert 'rain' in data['content']
