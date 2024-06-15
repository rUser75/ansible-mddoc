
# ansible-mddoc CLI Documentation

ansible-mddoc is a command-line tool that generates documentation from Ansible roles and playbooks. Below is the documentation for its usage.

## Usage

```shell

ansible-mddoc [project_directory] [options]
```

If project_directory is not specified, the current working directory will be used by default.
Options
Positional Arguments

    project_dir (optional): The project directory to scan. If not specified, the current working directory will be used.

Optional Arguments

    -C, --conf (optional): Specify a configuration file. If not specified, the default configuration file in the project directory will be used.

    --main-file: Specifies the main file for documenting a playbook. If not specified, tasks/main.yml will be used by default.

    -o: Define the destination folder for your documentation.

    -a: Set .yaml as the role files extension. By default, .yml files are parsed.

    -w: Clear the output directory without asking for confirmation.

    -y: Overwrite the output without asking for confirmation.

    --sample-config: Print the sample configuration YAML file and exit.

    -V, --version: Display the version of ansible-mddoc and exit.

Debugging Options

    -v: Set debug level to info.

    -vv: Set debug level to debug.

    -vvv: Set debug level to trace.

## Examples

Basic Usage

``` shell

ansible-mddoc /path/to/project
```
Generates documentation for the project located at /path/to/project.

Specifying a Configuration File

``` shell

ansible-mddoc /path/to/project -C /path/to/config.yml
```

Uses the specified configuration file config.yml.
Defining an Output Directory

```shell

ansible-mddoc /path/to/project -o /path/to/output
```
Saves the generated documentation to /path/to/output.

Specifying the Main File for a Playbook

```shell

ansible-mddoc /path/to/project --main-file playbook.yml
```
Uses playbook.yml as the main file for generating documentation.
Using .yaml Extension for Role Files

```shell

ansible-mddoc /path/to/project -a
```
Parses .yaml files instead of the default .yml.
Clearing the Output Directory Without Asking

```shell

ansible-mddoc /path/to/project -w
```
Clears the output directory without asking for confirmation.
Overwriting the Output Without Asking

``` shell

ansible-mddoc /path/to/project -y
```
Overwrites the existing output without asking for confirmation.
Printing the Sample Configuration

```shell

ansible-mddoc --sample-config
```
Prints the sample configuration YAML file and exits.
Displaying the Version

```shell

ansible-mddoc -V
```
Displays the version of ansible-mddoc and exits.
Setting Debug Levels

```shell

ansible-mddoc /path/to/project -vv
```
Sets the debug level to debug.
Exit Status

    0: Successful execution.
    Non-zero: An error occurred.


