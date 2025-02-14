import argparse
import socket
import types

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
parser = argparse.ArgumentParser(prog='elicit')
parser.add_argument('--env', choices=ENVIRONMENTS.keys(), default='prod',
                    help='Service environment to communicate with')
parser.add_argument('--env_file',
                    help='Environment file to load')
parser.add_argument('--api_url', type=str, default=None)
parser.add_argument('--ignore_https', action='store_true', default=False)
parser.add_argument('--debug', action='store_true', default=False)

parser.add_argument('--role', type=str, default='admin')
parser.add_argument('--user', type=str, default=None)
parser.add_argument('--password', type=str, default=None)
parser.add_argument('--client_id', type=str, default=None)
parser.add_argument('--client_secret', type=str, default=None)

def get_parser():
    return parser

def parse_command_line_args(custom_defaults=None):
    args = parser.parse_args()

    return types.SimpleNamespace(**add_command_line_args_default(args, custom_defaults))

def add_command_line_args_default(initial_args, custom_defaults=None):
    if custom_defaults is None:
        custom_defaults = {}

    if initial_args.api_url is None:
        initial_args.api_url = ENVIRONMENTS[initial_args.env]

    if initial_args.api_url.startswith('http://'):
        initial_args.ignore_https = True

    initial_args.send_opt = dict(verify=(not initial_args.ignore_https))

    return vars(initial_args) | custom_defaults
