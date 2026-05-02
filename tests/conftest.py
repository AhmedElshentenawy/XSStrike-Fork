"""
Pytest configuration and shared fixtures for XSStrike tests.

This module provides:
- Mock fixtures for HTTP requests
- Test data fixtures for payloads and responses
- Configuration setup for test environment
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import requests


@pytest.fixture
def mock_response():
    """
    Fixture: Creates a mock HTTP response object.
    
    Verifies: That mock responses can simulate realistic HTTP behaviors
    """
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.text = "Normal response content"
    response.headers = {"Content-Type": "text/html"}
    return response


@pytest.fixture
def mock_response_with_reflection():
    """
    Fixture: Creates a mock response with XSS probe reflection.
    
    Verifies: That responses containing injected probe strings are detected
    """
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.text = "User input: v3dm0s here is your reflection"
    response.headers = {"Content-Type": "text/html"}
    return response


@pytest.fixture
def mock_requester():
    """
    Fixture: Mocks the requester function to avoid real HTTP calls.
    
    Verifies: That test isolation prevents network requests during testing
    """
    with patch('core.requester.requester') as mock:
        yield mock


@pytest.fixture
def sample_params():
    """
    Fixture: Provides sample URL parameters for testing.
    
    Verifies: That parameter injection works with different data types
    """
    return {
        'q': 'search term',
        'id': '123',
        'username': 'testuser'
    }


@pytest.fixture
def sample_headers():
    """
    Fixture: Provides HTTP headers for test requests.
    
    Verifies: That headers are properly passed through the scanning pipeline
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Test)',
        'Accept': 'text/html',
        'Content-Type': 'application/x-www-form-urlencoded'
    }


@pytest.fixture
def sample_payloads():
    """
    Fixture: Provides XSS payloads for testing.
    
    Verifies: That different payload types are handled correctly
    """
    return [
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        '"><script>alert(1)</script>',
        "'; alert(1); //",
        '<iframe src=javascript:alert(1)>',
    ]


@pytest.fixture
def sample_response_html():
    """
    Fixture: Provides HTML response content for parser testing.
    
    Verifies: That HTML parsing correctly identifies injection contexts
    """
    return '''
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {reflection}</p>
        <script>
            var userInput = "{reflection}";
            console.log(userInput);
        </script>
        <div class="{reflection}">Result</div>
    </body>
    </html>
    '''
