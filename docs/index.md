# Introduction

Ansible-mddoc is a python package used to auto generate documentation for an ansible role and playbooks. It is a highly configurable tool and uses mdUtils to create the .md files.

## How does it work?

The package reads all tasks, handlers, defaults, variables, files and templates and produces equivalent .md files in the docs directory of the role.
If present also the roles|collections/requirements.yml are reads to obtain the list of requirements. 
It also allows you to configure it so that you can combine tasks, variables, templates, etc... into single .md files.

If the docs directory does not exist then it will be created.


### Tasks
- The package iterates over each of the tasks files, parsing the yaml to extract the "name" values and "tags" values from each task and writes it to the .md file. So good descriptions on the task names will lead to better documentation.
- In case of playbooks you can specify the which is you main file that can be have a different name from main.yml or it can be located outside of the tasks directory

- The package also generates a flow graph based on the include_tasks and import_tasks. This is useful in particular for larger roles to see the picture of how various task files are tied together. 
For a bettter matching please use the notation in fqcn (fully-qualified collection name and please use the following notation:
``` yaml
- name: include my external tasks file
  ansible.builtin.include_tasks:
    file: myTasksFile.yml
```  

### Variables
- The package iterates over all variables in the defaults and vars directories. To provide descriptions of the variables you can add the "@var:" annotation in the comment above the variable.
Is it possible to use a short form:

``` yaml
# @var: <variable_name>: <variable_description>
```
  or the extended form, if you want provide additional details:
``` yaml
# @var: 
# <variable_name>:
#   description: <variable_description>
#   <some_meta>: <some_value>
#   <some_other_meta>: <some_other_value>
# @var_end
```

For example:
``` yaml
# @var: my_var: This is a description of my variable!
```
- The package also identifies where the variable is used in the role and this is displayed under the "Where referenced" section under each variable. This is useful to see how the variables are used and also to identify if there are variables that are unused in the role.


### File Combination
- The package produce a single md file for each file in the tasks directory but is it possile combine them in single files
[File Combination](./file-combinations.md)
