# Variables

  
- To allow ansible-mddoc to identify comments relating to variables it is necessary to add the "@var:" annotation.
- The package also identifies where the variable is used in the role and this is displayed under the "Where referenced" section under each variable. This is useful to see how the variables are used and also to identify if there are variables that are unused in the role.


Is it possible to use a short form:

``` yaml
# @var: <variable_name>: <variable_description>
```

that will be displayed as 

___

## variable_name


variable_description
...

```

variable_value
...

```
___



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

```
# @var:
# proxy:
#   description:  proxy address to use
#   required: true
#   type: string
# @var_end
proxy: "http://myproxy.com:8080"
```

produce the following output

## proxy


proxy address to use
...

```

http://myproxy.com:8080
...

```
|Required|Type|Where referenced|
| :--- | :--- | :--- |
|true|string|<br/>|

---

If there are many var fields you may want to transpose the table for a better visual display. To do this set the transpose_variable_table variable to True in your configuration file. The output will then be displayed as follows:

<strong>minio_server_datadirs</strong>

Minio server data directory
...
  
```

/var/lib/minio
...
  
```
|Meta|Value|
| :--- | :--- |
|<strong>Type</strong>|string|
|<strong>Vault required</strong>|True|
|<strong>Where referenced</strong>|templates/minio.env.j2<br/>|



