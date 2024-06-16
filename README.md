# ansible-mddoc

ansible-mddoc is a package used to auto generate documentation for an ansible role and playbook. 

## To install
```
git clone https://github.com/rUser75/ansible-mddoc.git
cd ansible-mddoc
pip3 install .
```


## To run

Call ansible-mddoc passing in the path to the role
```
ansible-mddoc <path_to_role>
```



## Documentation

See [here](./docs/index.md) for full documentation.

## Credits


The idea for this project is based on (and includes some code from)

credit to them for their work:
  * [ansible-mdgen](https://github.com/murphypetercl/ansible-mdgen) by Peter Murphy
  * [ansible-autodoc](https://github.com/AndresBott/ansible-autodoc) by Andres Bott
