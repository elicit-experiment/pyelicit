from http import HTTPStatus
from . import api
import pprint
import re
import json
import random
import string
import yaml

_pp = pp = pprint.PrettyPrinter(indent=4)

def proxy_print(fmt, **args):
    print(fmt, **args)

setattr(pp, 'print', proxy_print)

def search(d, key, default=None):
    """Return a dict containing to the specified key in the (possibly
    nested) within dictionary d. If there is no item with that key, return
    default.
    """
    stack = [d]
    while stack:
        cur_d = stack[-1]
        stack.pop()
        for k, v in cur_d.items():
            if k == key:
                return cur_d
            elif isinstance(v, dict):
                stack.append(v)
    return default


# camelCase to snake_case
def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# Parse the pagination link headers out of the HTTP response
def parse_pagination_links(link_header):
    pp.pprint(link_header)
    link = link_header[0].split(',')
    link_matches = [re.match(r'\s*<([^>]+)>;\s*rel="([a-z]+)"', x) for x in link]
    links = [dict(href=m.group(1), rel=m.group(2)) for m in link_matches]
    last_page_link = list(filter(lambda link: link['rel'] == 'last', links))
    next_page_link = list(filter(lambda link: link['rel'] == 'next', links))
    return last_page_link, next_page_link

def assert_role(client, elicit, role = 'admin'):
    resp = client.request(elicit['getCurrentUser']())

    assert resp.status == HTTPStatus.OK

    print("Current User:")
    pp.pprint(resp.data)

    user = resp.data

    if isinstance(role, list):
        assert (resp.data.role in role)
    else:
        assert (resp.data.role == role)

    return user

def add_users_to_protocol(client, elicit, new_study, new_protocol_definition, study_participants, group_name_map=None):
    protocol_users = []
    for user in study_participants:
        group_name = group_name_map[user.username] if group_name_map else None
        protocol_user = dict(protocol_user=dict(user_id=user.id,
                                                study_definition_id=new_study.id,
                                                group_name=group_name,
                                                protocol_definition_id=new_protocol_definition.id))
        resp = client.request(elicit['addProtocolUser'](
            protocol_user=protocol_user,
            study_definition_id=new_study.id,
            protocol_definition_id=new_protocol_definition.id))

        assert resp.status == HTTPStatus.CREATED
        protocol_users.append(resp.data)
    return protocol_users


def find_or_create_user(client, elicit, username, password, email=None, role=None):
    resp = client.request(elicit['findUser'](id=username))

    if resp.status == HTTPStatus.NOT_FOUND:
        pp.pprint(resp.data)
        pp.pprint(resp.status)
        print("Not found; Creating user:")
        user_details = dict(username=username,
                            password=password,
                            email=email or (username + "@elicit.com"),
                            role=role or 'registered_user',
                            password_confirmation=password)
        resp = client.request(elicit['addUser'](user=dict(user=user_details)))
        return (resp.data)
    else:
        print("User already exists.")
        return (resp.data)


def add_object(client, elicit, operation, pp = _pp, **args):
    definition_data_parent = search(args, 'definition_data')
    if definition_data_parent:
        if isinstance(definition_data_parent['definition_data'], dict):
            definition_data_parent['definition_data'] = json.dumps(definition_data_parent['definition_data'])
    resp = client.request(elicit[operation](**args))
    assert resp.status == HTTPStatus.CREATED
    if resp.status != HTTPStatus.CREATED:
        return (None)

    created_object = resp.data
    if pp != None:
        pp.print("\n\nCreated new object with %s:\n" % operation)
        pp.pprint(created_object)

    return (created_object)


def find_objects(client, elicit, operation, pp = _pp, **args):
    next_link = True
    last_page = ""
    found_objects = []
    page = 0
    pagination_aware = 'page' in args
    while next_link:
        page += 1

        if not pagination_aware:
            page_size = args['page_size'] if 'page_size' in args else 3
            args = dict(args, page=page, page_size=page_size)

        resp = client.request(elicit[operation](**args))

        assert resp.status == HTTPStatus.OK
        if resp.status != HTTPStatus.OK:
            return None

        next_link = False
        result_len = len(resp.data)
        if result_len > 0:
            link_header = resp.header['Link'] if 'Link' in resp.header else []
            if not pagination_aware:
                if list(filter(None, link_header)):
                    last_page_link, next_page_link = parse_pagination_links(link_header)

                    if len(last_page_link) == 1:
                        last_page = re.search(r'.*page=(\d+).*', last_page_link[0]['href']).group(1)
                        if pp is not None:
                            pp.print("last_page (%s)" % last_page)

                    if len(next_page_link) == 1:
                        next_link = bool(next_page_link[0]['href'])
                        if pp is not None:
                            pp.pprint("found next page link (%s)"%next_page_link[0]['href'])
                elif result_len >= page_size:
                    #  no header, but full page. N+1 risk
                    if pp is not None:
                        pp.print("Full page: %d/%d; getting next page" % (result_len, page_size))
                    next_link = True

            found_objects += resp.data

    if pp is not None:
        pp.print("\n\nFound objects with %s(%s) in %d/%s pages:\n" % (operation, args, int(page), last_page))
        pp.pprint(found_objects)

    return found_objects

def get_object(client, elicit, operation, pp = _pp, **args):
    resp = client.request(elicit[operation](**args))
    assert resp.status == HTTPStatus.OK
    if resp.status != HTTPStatus.OK:
        return (None)

    found_object = resp.data
    if pp != None:
        pp.print("\n\nGot object with %s(%s):\n" %(operation, args))
        pp.pprint(found_object)

    return (found_object)

def load_trial_definitions(file_name):
    with open(file_name, 'r') as tdfd:
        lines = tdfd.readlines()
        td = "\n".join(lines)
        _locals = locals()
        exec(td, globals(), _locals)
        return _locals['trial_components']

def load_yaml_from_env(env):
    # Construct the filename dynamically based on env
    yaml_file = f"{env}.yaml"

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


class Elicit:
    """
    Constructor for the Elicit class.

    Initializes an instance of Elicit using the provided configuration object.

    Arguments:
        configuration (dict): Configuration object containing the following attributes:
            - env (str): Environment identifier (default: 'prod').
            - apiurl (str): Base URL for the API (default: 'https://elicit-experiment.com').
            - ignore_https (bool): Whether to bypass HTTPS verification (default: False).
            - debug (bool): Whether to enable debug mode (default: False).
            - role (str): Role of the user (default: 'admin').
            - username (str, optional): Username for authentication.
            - password (str, optional): Password for authentication.
            - client_id (str, optional): Client ID for authentication.
            - client_secret (str, optional): Client secret for authentication.
            - send_opt (dict, optional): Additional options for API requests (default: {'verify': True}).

    Raises:
        FileNotFoundError: If the environment YAML file is not found during credential loading.
        yaml.YAMLError: If the environment YAML file contains invalid YAML.

    Behavior:
        - If a username is provided, it assumes all the credentials (username, password, client_id, and client_secret) are specified.
        - Otherwise, it loads credentials from an environment-specific YAML file (e.g. `prod.yaml`) located in the same directory as this script.
        - Initializes the ElicitApi object with the defined credentials and configuration.
        - Logs in to the ElicitApi and creates a client object for further API interactions.
    """


def add_find_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return find_objects(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)

def add_get_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return get_object(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)

def add_add_api_fn(api_name):
    fn_name = camel_to_snake(api_name)

    def fn(self, **kwargs):
        return add_object(self.client, self.elicit_api, api_name, self.pp(), **kwargs)

    setattr(Elicit, fn_name, fn)

for api_name in ['findStudyResults', 'findExperiments', 'findStages', 'findDataPoints', 'findTimeSeries',
                 'findTrialResults', 'findComponents', 'findTimeSeries', 'findStudyDefinitions']:
    add_find_api_fn(api_name)

for api_name in ['addStudy', 'addProtocolDefinition', 'addPhaseDefinition', 'addTrialDefinition', 'addTrialOrder',
                 'addPhaseOrder', 'addProtocolUser', 'addComponent', 'addUser']:
    add_add_api_fn(api_name)

for api_name in ['getComponent']:
    add_get_api_fn(api_name)
