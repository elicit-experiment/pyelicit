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

## Configuration

Secrets and other settings can be configured explicitly via arguments to the `Elicit` constructor, or implicitly via yaml files.

The `env` configuration parameter controls the base name of the credential file to be loaded. By default, this is `prod`. The package will then load the configuration file `<env>.yaml`. This file may be placed in several places; the search order is as follows:
1. The current working directory when the `Elicit` object is created
2. The directory in which the script creating the elicit object is located
3. The home directory folder `~/.config/elicit/`

Alternatively, the `env_file` parameter lets one specify the file directly.

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
python -m pytest tests/
```