import pprint

class ElicitCreds:
    """
    Class defining credentials to communicate with the Elicit service
    """
    PUBLIC_CLIENT_ID = 'admin_public'
    PUBLIC_CLIENT_SECRET = 'czZCaGRSa3F0MzpnWDFmQmF0M2JW'
    ADMIN_USER = 'pi@elicit.com'
    ADMIN_PASSWORD = 'password'

    def __init__(self,
                 _user=ADMIN_USER,
                 _password=ADMIN_PASSWORD,
                 _public_client_id=PUBLIC_CLIENT_ID,
                 _public_client_secret=PUBLIC_CLIENT_SECRET):
        """
        Initialize
        :param _admin_user: The (typically admin) user name
        :param _admin_password: The password
        :param _public_client_id: The OAuth Client ID
        :param _public_client_secret: The OAuth client secret
        :return: returns nothing
        """
        self.user = _user
        self.password = _password
        self.public_client_id = _public_client_id
        self.public_client_secret = _public_client_secret

    def __str__(self):
        return pprint.pformat(vars(self))

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_env(cls, config):
        # Return None unless all required fields are specified
        required_fields = ['user', 'password', 'client_id', 'client_secret']
        if not all((field in config) and (config[field] is not None) for field in required_fields):
            return None

        return cls(config['user'], config['password'], config['client_id'], config['client_secret'])
