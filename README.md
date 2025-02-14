# pyelicit

## Installation

(Assuming `uv`, update as appropriate for your package manager)

```
uv pip install git+https://github.com/elicit-experiment/pyelicit/#subdirectory=pyelicit
```

## Development Setup

For development, clone the repository and install in editable mode with test dependencies:

```bash
git clone https://github.com/elicit-experiment/pyelicit.git
cd pyelicit
python -m pip install -e .
```

## Running Tests

To run the test suite:

```bash
python -m pytest tests/
```

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


## Tests

```bash
uv pip install -e ".[test]"
```