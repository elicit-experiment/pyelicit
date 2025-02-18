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

Elicit objects are typically created via:

```
elicit_object = elicit.Elicit(parse_command_line_args(arg_defaults))
```

This building process combines three sources of data:

2. **Defaults**: Values explicitly provided in the `arg_defaults` dictionary during parser initialization.
2. **Command-Line Arguments**: Values directly provided by the user, via the `argparse` package.
3. **File-Based Configuration (Optional)**:
    - If `--env_file` is provided, the script attempts to load a specific `.yaml` file via `load_yaml_from_env_file()`.
    - If `--env` is specified (e.g., `local`, `prod`), the script infers the YAML file name (`<env>.yaml`)

Each data source is merged in a hierarchical manner, where data from sources specified by the user (command-line arguments) takes precedence over defaults, and file-based configurations takes precedence over both default and command-line arguments.

In the case of `--env` above, the package looks for the environment file in the following paths:

1. The current working directory when the `Elicit` object is created
2. The directory in which the script creating the elicit object is located
3. The home directory folder `~/.config/elicit/`

Whether discovered via that process or specified directly, the environment file has the following format:

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