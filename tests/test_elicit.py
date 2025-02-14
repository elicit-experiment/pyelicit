import pytest

from pyelicit.elicit import Elicit, config_search_paths
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from pprint import pprint
from pyelicit.command_line import add_command_line_args_default, get_parser
import os
from pathlib import Path

def test_elicit_constructor_with_direct_config():
    """Test Elicit constructor with directly provided configuration"""
    config = SimpleNamespace(
        env_file=None,
        env=None,
        api_url='https://test.com',
        user='test_user',
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
        assert elicit.creds.user == 'test_user'
        assert elicit.creds.password == 'test_pass'
        assert elicit.creds.public_client_id == 'test_client'
        assert elicit.creds.public_client_secret == 'test_secret'
        
        # Verify API was initialized correctly
        mock_api.assert_called_once()
        mock_api_instance.login.assert_called_once()

def test_elicit_constructor_missing_credentials():
    """Test Elicit constructor fails appropriately with missing credentials"""
    config = SimpleNamespace(
        env_file=None,
        env='prod',
        api_url='https://test.com',
        user=None,
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
    config = {
        'env_file': 'test_env.yaml',
        'env': 'prod',
        'api_url': 'https://test.com',
        'user': 'config_user',
        'client_id': 'config_client',
    }
    
    mock_file_config = {
        'user': 'file_user',
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

            args = []
            for k, v in config.items():
                args.append(f'--{k}')
                args.append(v)

            parsed_args = add_command_line_args_default(get_parser().parse_args(args))
            pprint(parsed_args)
            elicit = Elicit(parsed_args)

        assert elicit.creds.user == 'config_user'
        assert elicit.creds.password == 'file_pass'
        assert elicit.creds.public_client_id == 'config_client'
        assert elicit.creds.public_client_secret == 'file_secret'

def test_config_search_paths():
    search_paths = config_search_paths()
    assert len(search_paths) == 3
    assert search_paths[0] == '.'
    assert search_paths[1].endswith("pytest")
    assert search_paths[2] == str(Path.home() / ".config/elicit")

def test_add_custom_command_line_defaults():
    config = {
        'env_file': 'test_env.yaml',
        'env': 'prod',
        'api_url': 'https://test.com',
        'user': 'config_user',
        'client_id': 'config_client',
    }

    mock_file_config = {
        'user': 'file_user',
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

            args = []
            for k, v in config.items():
                args.append(f'--{k}')
                args.append(v)

            parsed_args = add_command_line_args_default(get_parser().parse_args(args), {'client_id': 'custom_client_id'})
            pprint(parsed_args)
            elicit = Elicit(parsed_args)

        assert elicit.creds.user == 'config_user'
        assert elicit.creds.password == 'file_pass'
        assert elicit.creds.public_client_id == 'custom_client_id'
        assert elicit.creds.public_client_secret == 'file_secret'
