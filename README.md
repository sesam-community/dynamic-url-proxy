# dynamic-url-proxy
Microservice for generating dynamic urls

This microservice can be used to
  * dynamically build url based on some function evaluation

Main idea behind is that filenames or urls might have -for instance- datetime related fix in their names. With this microservice you can build a url in "replace substring" manner and forward the call as if you are calling it directly.

#How-TO
For every dynamic part in your url:
  * replace it by [<part_name>]
  * add a query parameter <part_name>=<python_function_to_be_evaluated>

It is only datetime module that are made available to 'eval' additonally to builtins module. You will have to customize after your needs, if any.

### example config in SESAM
system:
```
{
    "_id": "my-dynamic-url-proxy",
    "type": "system:microservice",
    "connect_timeout": 60,
    "docker": {
        "environment": {
            "LOGLEVEL": "DEBUG",
            "PORT": 5000
        },
        "image": "sesamcommunity/dynamic-url-prox:v1.0",
        "port": 5000
    },
    "read_timeout": 7200
}

```
pipe:
```
...
...
,
    "source": {
        "type": "json",
        "system": "my-dynamic-url-proxy",
        "url": "/?url=http://my-server:5000/my_file-[replace_me].csv&replace_me=datetime.datetime.now().replace(day=1).strftime('%Y%m%d')"
    },
...
...
```
