# Python-openam

Python-openam is a REST client for OpenAM servers.
The API implemented is described [here](https://wikis.forgerock.org/confluence/display/openam/Use+OpenAM+RESTful+Services)



## Install

```
$ git clone https://github.com/pfreixes/python-openam
$ cd pyton-openam
$ python setup.py install
```

## Quick Usage

```python
>>> from openam import restclient
>>> c = restclient.Client("http://openam.example.com:8080/openam-server/", "demo", "*****")
>>> c.token_id
AQIC5wM2LY4SfczncpY2PEufFAyRqXP2oW_Qkb_g80AgNOw.*AAJTSQACMDEAAlNLABM0Mjk0NDEwMjA5asdfMzM1NjY3NTUy*
>>> c.attributes("mail")
[{"mail" : "foo@gmail.com"}]
>>> c.set_attribute("mail", "test@gmail.com")
>>> c.attributes("mail")
```

## Other

Thanks to [Oriol Rius](https://github.com/oriolrius) for fund this project, Standing on the shoulders of giants
