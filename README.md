# Python-openam

Python-openam is a REST client for OpenAM servers where this
implement the API described [here](https://wikis.forgerock.org/confluence/display/openam/Use+OpenAM+RESTful+Services)



## Install

```
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

Thanks to [OriolRius](https://github.com/oriolrius) for fund this project, Standing on the shoulders of giants
