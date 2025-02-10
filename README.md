# pyelicit

## Secrets Configuration

Secrets can be configured explicitly via arguments to the `Elicit` constructor, or implicitly via yaml files.

The `env` configuration field controls which credential file is loaded. By default, this is `prod`. 

These files have the following format:

<env>.yaml:

```yaml
client_id: <client id>
client_secret: <client secret>
user: <user email>
password: <user password>
```

`client_id` and `client_secret` are the OAuth application for the configured on the server.

`user` and `password` are the user name/password for the identity to be used to make the API calls. 

