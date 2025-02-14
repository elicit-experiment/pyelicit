import pytest
from pyelicit.elicit import Elicit
from unittest.mock import MagicMock, patch
from types import SimpleNamespace

def test_elicit_constructor_with_direct_config():
    """Test Elicit constructor with directly provided configuration"""
    config = SimpleNamespace(
        env_file=None,
        env='prod',
        apiurl='https://test.com',
        username='test_user',
        password='test_pass',
        client_id='test_client',
        client_secret='test_secret',
        send_opt={'verify': True},
        debug=False
    )
    
    with patch('pyelicit.elicit.api.ElicitApi') as mock_api:
        # Setup mock API
        mock_api_instance = MagicMock()
        mock_api_instance.login.return_value = MagicMock()
        mock_api.return_value = mock_api_instance
        
        # Create Elicit instance
        elicit = Elicit(config)
        
        # Verify credentials were created correctly
        assert elicit.creds.username == 'test_user'
        assert elicit.creds.password == 'test_pass'
        assert elicit.creds.client_id == 'test_client'
        assert elicit.creds.client_secret == 'test_secret'
        
        # Verify API was initialized correctly
        mock_api.assert_called_once()
        mock_api_instance.login.assert_called_once()

def test_elicit_constructor_missing_credentials():
    """Test Elicit constructor fails appropriately with missing credentials"""
    config = SimpleNamespace(
        env_file=None,
        env='prod',
        apiurl='https://test.com',
        username=None,
        password=None,
        client_id=None,
        client_secret=None,
        send_opt={'verify': True},
        debug=False
    )
    
    with patch('pyelicit.elicit.load_yaml_from_env') as mock_load:
        mock_load.return_value = None
        
        with pytest.raises(Exception, match="Credentials not found"):
            Elicit(config)

def test_elicit_constructor_with_env_file():
    """Test Elicit constructor loading configuration from environment file"""
    config = SimpleNamespace(
        env_file='test_env.yaml',
        env='prod',
        apiurl='https://test.com',
        username=None,
        password=None,
        client_id=None,
        client_secret=None,
        send_opt={'verify': True},
        debug=False
    )
    
    mock_file_config = {
        'username': 'file_user',
        'password': 'file_pass',
        'client_id': 'file_client',
        'client_secret': 'file_secret'
    }
    
    with patch('pyelicit.elicit.load_yaml_from_env_file') as mock_load:
        mock_load.return_value = mock_file_config
        
        with patch('pyelicit.elicit.api.ElicitApi') as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.login.return_value = MagicMock()
            mock_api.return_value = mock_api_instance
            
            elicit = Elicit(config)
            
            assert elicit.creds.username == 'file_user'
            assert elicit.creds.password == 'file_pass'
            assert elicit.creds.client_id == 'file_client'
            assert elicit.creds.client_secret == 'file_secret'
