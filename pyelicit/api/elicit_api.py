from pyswagger import App, Security
from pyswagger.contrib.client.requests import Client
import ssl
import tempfile
from . import elicit_creds
from contextlib import contextmanager
import urllib.error
import urllib.request
import requests
import os
from urllib.parse import urlparse
from pathlib import Path

@contextmanager
def user_agent_context(user_agent):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', user_agent)]
    urllib.request.install_opener(opener)
    yield
    urllib.request.install_opener(None)

# HACK to work around self-signed SSL certs used in development
def dont_check_ssl():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

class ElicitApi:
    PRODUCTION_URL = 'https://elicit-experiment.com/'

    def __init__(self,
                 creds=elicit_creds.ElicitCreds(),
                 api_url=PRODUCTION_URL,
                 send_opt=dict(verify=True)):

        print("Initialize Elicit client library for %s" % api_url)
        print("Initialize Elicit client library for {} {}".format(creds.user, creds.password))
        print("Initialize Elicit client library for {} {}".format(creds.public_client_id, creds.public_client_secret))
        print("Request options: {}\n".format(send_opt))

        if (not send_opt['verify']) and api_url.startswith("https"):
            print('WARNING: not checking SSL')
            dont_check_ssl()

        self.api_url = api_url
        with user_agent_context('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'):
            self.swagger_url = self.api_url + '/apidocs/v1/swagger.json'

        try:
            # Load self.swagger_url json file to local filesystem
            print(f"Downloading swagger definition from {self.swagger_url}")
            response = requests.get(self.swagger_url)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_file:
                temp_file.write(response.content)
                swagger_json_local_path = temp_file.name
                print(f"Saved swagger.json to temporary file {swagger_json_local_path}")

            # Creating a URL string pointing to the temporary file
            swagger_json_url = Path(swagger_json_local_path).as_uri()

            print(f"Connecting to Elicit API Swagger definition #{swagger_json_url} downloaded from {self.swagger_url}")
            self.app = App.create(swagger_json_url)  # now valid on all OS
            print(f"Loaded API definition {self.swagger_url}")
            self.auth = Security(self.app)
            self.creds = creds

            # init swagger client
            self.client = Client(self.auth,
                                 send_opt=send_opt)  # HACK to work around self-signed SSL certs used in development

            self.api_host = urlparse(self.api_url).netloc

            if self.app.root.host != self.api_host:
                print('WARNING: API URL from swagger doesn\'t match this configuration: [%s] vs [%s]'%(self.api_url, self.app.root.host))

        except urllib.error.HTTPError as e:
            # If the server returns an HTTP error (like 403 Forbidden), it will be
            # caught here.
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
            print('Error message: ', e.read())
            raise PermissionError('Cannot load swagger file {} {}.'.format(e.code, e.reason))

    def login(self):
        """
        Login to Elicit using credentials specified in init
        :return: client with auth header added.
        """
        auth_request = dict(client_id=self.creds.public_client_id,
                            client_secret=self.creds.public_client_secret,
                            grant_type='password',
                            email=self.creds.user,
                            password=self.creds.password)
        print(auth_request)
        resp = self.client.request(self.app.op['getAuthToken'](auth_request=auth_request))

        print(resp.status)
        assert resp.status == 200

        self.auth = resp.data
        self.auth_header = 'Bearer ' + self.auth.access_token
        self.client._Client__s.headers['Authorization'] = self.auth_header

        return self.client

    def __getitem__(self, op):
        return lambda **args: self.app.op[op](**(self.bind_auth(args)))

    def bind_auth(self, args):
        args.update(authorization=self.auth_header)
        return args
