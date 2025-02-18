import pytest

from pyelicit.elicit import Elicit
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from pprint import pprint
from pyelicit.command_line import add_command_line_args_default, get_parser, config_search_paths
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
    
    with patch('pyelicit.command_line.load_yaml_from_env') as mock_load:
        mock_load.return_value = None
        
        with pytest.raises(Exception, match="Credentials not found"):
            Elicit(config)

def test_elicit_constructor_with_env_file():
    """Test Elicit constructor loading configuration from environment file"""
    command_line_args = {
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
    
    with patch('pyelicit.command_line.load_yaml_from_env_file') as mock_load:
        mock_load.return_value = mock_file_config
        
        with patch('pyelicit.elicit.api.ElicitApi') as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.login.return_value = MagicMock()
            mock_api.return_value = mock_api_instance

            args = []
            for k, v in command_line_args.items():
                args.append(f'--{k}')
                args.append(v)

            parsed_args = add_command_line_args_default(get_parser().parse_args(args))
            elicit = Elicit(parsed_args)

        # File should override.
        assert elicit.creds.user == 'file_user'
        assert elicit.creds.password == 'file_pass'
        assert elicit.creds.public_client_id == 'file_client'
        assert elicit.creds.public_client_secret == 'file_secret'

def test_config_search_paths():
    search_paths = config_search_paths()
    assert len(search_paths) == 3
    assert search_paths[0] == '.'
    assert search_paths[1].endswith("pytest")
    assert search_paths[2] == str(Path.home() / ".config/elicit")

def test_add_custom_command_line_defaults():
    command_line_args = {
        'env_file': 'test_env.yaml',
        'env': 'prod',
        'api_url': 'https://test.com',
        'user': 'config_user',
        'client_secret': 'config_secret',
    }

    mock_file_config = {
        'user': 'file_user',
        'password': 'file_pass',
    }

    with patch('pyelicit.command_line.load_yaml_from_env_file') as mock_load:
        mock_load.return_value = mock_file_config

        with patch('pyelicit.elicit.api.ElicitApi') as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.login.return_value = MagicMock()
            mock_api.return_value = mock_api_instance

            args = []
            for k, v in command_line_args.items():
                args.append(f'--{k}')
                args.append(v)
            args.append('--debug')

            parsed_args = add_command_line_args_default(get_parser().parse_args(args), {'user': 'custom_user', 'client_id': 'custom_client_id', 'client_secret': 'custom_secret'})
            pprint(parsed_args)
            elicit = Elicit(parsed_args)

        # File overrides custom defaults
        assert elicit.creds.user == 'file_user'
        assert elicit.creds.password == 'file_pass'
        # custom default overrides if command line is not specified
        assert elicit.creds.public_client_id == 'custom_client_id'
        # if command line is specified (but not file), it wins
        assert elicit.creds.public_client_secret == 'config_secret'



def test_override_env():
    """Test that the environment can be overridden. This was not the previous behavior"""
    command_line_args = {
        'env': 'local',
    }

    mock_file_config = {
        'user': 'file_user',
        'password': 'file_pass',
        'client_id': 'file_client',
        'client_secret': 'file_secret'
    }

    with patch('pyelicit.command_line.load_yaml_from_env') as mock_load:
        mock_load.return_value = mock_file_config

        with patch('pyelicit.elicit.api.ElicitApi') as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.login.return_value = MagicMock()
            mock_api.return_value = mock_api_instance

            args = []
            for k, v in command_line_args.items():
                args.append(f'--{k}')
                args.append(v)

            parsed_args = add_command_line_args_default(get_parser().parse_args(args))
            pprint(parsed_args)
            elicit = Elicit(parsed_args)

        mock_load.assert_called_with('local')

        assert elicit.creds.user == 'file_user'
        assert elicit.creds.password == 'file_pass'
        assert elicit.creds.public_client_id == 'file_client'
        assert elicit.creds.public_client_secret == 'file_secret'
