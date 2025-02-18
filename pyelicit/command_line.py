import argparse
import socket
import types
import yaml
import pprint
import sys
import os
from pathlib import Path

pp = pprint.PrettyPrinter(indent=4)

# grab the address using socket.getaddrinfo
answers = socket.getaddrinfo('elicit-experiment.com', 443)
ip4_answers = list(filter(lambda x: x[0] == socket.AF_INET, answers))

(family, type, proto, canon_name, (prod_ip_address, port)) = ip4_answers[0]

ENVIRONMENTS = {
    'local': 'http://localhost:3000',
    'local_docker': 'http://elicit.docker.local',
    'prod': "https://elicit-experiment.com",
    'prod_ip': "https://%s"%(str(prod_ip_address))
}
parser = None

def init_parser(custom_defaults={}):
    """
    Initializes or reinitializes and configures the argument parser for the application.

    :return: Configured argparse.ArgumentParser instance.
    :rtype: argparse.ArgumentParser
    """
    global parser
    parser = argparse.ArgumentParser(prog='elicit')
    parser.add_argument('--env', choices=ENVIRONMENTS.keys(), default=custom_defaults.get('env') or None,
                        help='Service environment to communicate with')
    parser.add_argument('--env_file', default=custom_defaults.get('env_file') or None,
                        help='Environment file to load')
    parser.add_argument('--api_url', type=str, default=custom_defaults.get('api_url') or None)
    parser.add_argument('--ignore_https', action='store_true', default=custom_defaults.get('ignore_https') or False)
    parser.add_argument('--debug', action='store_true', default=custom_defaults.get('debug') or False)

    parser.add_argument('--role', type=str, default=custom_defaults.get('role') or 'admin')
    parser.add_argument('--user', type=str, default=custom_defaults.get('user') or None)
    parser.add_argument('--password', type=str, default=custom_defaults.get('password') or None)
    parser.add_argument('--client_id', type=str, default=custom_defaults.get('client_id') or None)
    parser.add_argument('--client_secret', type=str, default=custom_defaults.get('client_secret') or None)

    return parser

def config_search_paths():
    search_paths = [
        ".",  # Current directory
        str(get_current_script_dir()),  # Directory of the executing script
        str(Path.home() / ".config/elicit")  # '.config/elicit' subdirectory of the user's home
    ]
    return search_paths


def load_yaml_from_env(env):
    # Construct the filename dynamically based on env
    yaml_file = f"{env}.yaml"
    search_paths = config_search_paths()

    for path in search_paths:
        if path is None:
            continue
        file_path = os.path.join(path, yaml_file)
        if os.path.isfile(file_path):
            return load_yaml_from_env_file(file_path)

    print(f"Error: File '{yaml_file}' not found in any of the search paths. Search paths: {search_paths}")
    return None

def load_yaml_from_env_file(yaml_file):
    # Load and parse the YAML file
    try:
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"Error: File '{yaml_file}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{yaml_file}': {e}")
        return None

def get_current_script_dir():
    """Gets the directory of the top-level (main) executing script.

    Returns:
        pathlib.Path or None: The directory as a pathlib.Path object, or None
                             if it cannot be determined.
    """
    try:
        # Check if running interactively. If so, return None
        if not hasattr(sys, 'argv') or not sys.argv:
            return None

        # Get the absolute path of the main script
        main_script_path = os.path.abspath(sys.argv[0])

        # Return the directory as a Path object
        return Path(os.path.dirname(main_script_path))

    except Exception as e:  # Catch any unexpected errors
        return None

def get_parser():
    return parser

def parse_command_line_args(custom_defaults=None):
    if custom_defaults is None:
        custom_defaults = {}

    args = parser.parse_args()

    return types.SimpleNamespace(**add_command_line_args_default(args, custom_defaults))

def add_command_line_args_default(initial_args, custom_defaults={}):
    configuration = initial_args
    if not isinstance(initial_args, dict):
        configuration = vars(initial_args)

    # load configuration from file.
    configuration_from_file = None
    if configuration['env_file'] is not None:
        configuration_from_file = load_yaml_from_env_file(configuration['env_file'])
    elif configuration['env'] is not None:
        configuration_from_file = load_yaml_from_env(configuration['env'])

    if configuration['debug']:
        print("Configuration from file:")
        pp.pprint(configuration_from_file)
        print("Configuration from command line + defaults:")
        pp.pprint(configuration)

    # Merge configuration and configuration_from_file into effective_configuration
    effective_configuration = configuration | (configuration_from_file or {})

    # Update configuration with custom_defaults where applicable
    for key in effective_configuration.keys():
        if key in custom_defaults and effective_configuration[key] is None and custom_defaults[key] is not None:
            effective_configuration[key] = custom_defaults[key]

    if configuration['debug']:
        print("Effective configuration:")
        pp.pprint(effective_configuration)

    # Add infer-able argument defaults
    if effective_configuration.get('api_url') is None:
        if effective_configuration.get('env') is None:
            raise Exception("Either --env or --api_url must be specified")
        effective_configuration['api_url'] = ENVIRONMENTS[effective_configuration['env']]

    if effective_configuration['api_url'].startswith('http://'):
        effective_configuration['ignore_https'] = True

    effective_configuration['send_opt'] = dict(verify=(not effective_configuration.get('ignore_https')))

    
    return effective_configuration

init_parser()
