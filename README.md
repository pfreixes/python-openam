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

## Run Tests
```
$ unit2 discover
......
----------------------------------------------------------------------
Ran 6 tests in 0.008s

OK
pfreixes@pfreixes-laptop-linux:~/programs/python-openam{master}$ unit2 discover -v
test_attributes (openam.tests.test_restclient.RestClientTestCase) ... ok
test_authentication (openam.tests.test_restclient.RestClientTestCase) ... ok
test_authentication_failed (openam.tests.test_restclient.RestClientTestCase) ... ok
test_logout (openam.tests.test_restclient.RestClientTestCase) ... ok
test_set_attribute (openam.tests.test_restclient.RestClientTestCase) ... ok
test_valid_token (openam.tests.test_restclient.RestClientTestCase) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.008s

OK
```


## Other

Thanks to [Oriol Rius](https://github.com/oriolrius) for fund this project, Standing on the shoulders of giants
