import pytest
from app import app as flask_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    yield flask_app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_register_usecase(mocker):
    """Mock the register usecase."""
    return mocker.patch('usecases.auth_usecase.register')

@pytest.fixture
def mock_login_usecase(mocker):
    """Mock the login usecase."""
    return mocker.patch('usecases.auth_usecase.login')