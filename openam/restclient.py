#  Pau Freixes, pfreixes@gmail.com
#  2013-08
#
#  Thanks to Oriol Rius for fund this piece of code
"""Client rest interface for OpenAM server. This guide follow current
documentation of OpenAM Rest interface, you can get it from next url

https://wikis.forgerock.org/confluence/display/openam/Use+OpenAM+RESTful+Services

Usage of this module might look like this:

>> from openam import restclient
>> client = restclient.Client("http://host:port/openamresource",
                               "username", "password")
>> print client.token_id
AQIC5wM2LY4Sfcy8a-eXHlPdvTfXo-HLxs761OviSVrRFlg.*AAJTSQACMDEAAlNLABQtNDg3MTMxNjI2MzA5NDM0MTYzOQ..*
>> client.logout()
"""

import requests
import urllib
import re

# Token value is a string with the character '*',
# and requests use urlib.quote to quote all non printable
# chars turning it in %2A. OpenAM server doent understand
# it. Therefore we have to bypass this.
# Looking forward to fix that moving to another http client
_quote = urllib.quote


def patched_quote(x, safe):
    safe = "/*"
    if safe is not None:
        return _quote(x, safe="/*")

urllib.quote = patched_quote

def urljoin(base, resource):
    return base + resource


class ClientException(Exception):
    """
    Main Exception raised when Client interface fails
    due a internal and none specific raesons, use just
    to get more info about exception.

    >> client = restclient.Client(url, user, password)
    >> try:
    >>     client.set_attribute("mail", "foo@gmail.com")
    >> except ClientUnauthorized:
    >>     print "You have no permisisons to do that"
    >> except ClientException, c:
    >>     print str(c)
    >>     raise c
    """
    def __init__(self, status_code, description):
        self.status_code = status_code
        Exception.__init__(self, description)

class ClientAuthenticationFailed(Exception):
    """
    Exception raised when Client can't be 
    authenticated with ones credentials
    """
    pass

class ClientUnauthorized(Exception):
    """
    Exception raised when Client interface has no 
    privilegies to make some action
    """
    pass


class Client:
    """
    Client rest implementation to comunicate with one OpenAm service
    """

    _auth_resource = "/identity/authenticate"
    _logout_resource = "/identity/logout"
    _token_resource = "/identity/isTokenValid"
    _attribute_resource = "/identity/attributes"
    _set_attribute_resource = "/identity/update"

    def __init__(self, url, username, password):
        """
        Create one Rest Client against url server with one already authenticated 
        sesion with username and password values. 
        """
        if url[-1] == "/":
            self._url = url[:-1]
        else:
            self._url = url

        r = requests.get(urljoin(self._url, Client._auth_resource),
                         params={"username": username, "password": password})

        if r.status_code != requests.status_codes.codes.ok:
            raise ClientAuthenticationFailed()

        try:
            _, token_id = r.text.split("=")
            token_id = token_id.strip(" \r\n")
        except Exception, e:
            raise ClientException(r.status_code, 
                                  "Some error has ocurred getting the token value from %s" % r.text)

        self._token_id = token_id
        self._username = username

    @property
    def token_id(self):
        return self._token_id

    @property
    def username(self):
        return self._username

    def _parse_invalid_request(self, text):
        class_path = description = ""

        if text:
            # sometimes we have mor info
            try:
                _, mixed_info = text.split("=")
                class_path = mixed_info.split(" ")[0]
                description = " ".join(mixed_info.split(" ")[1:])
            except Exception, e:
                pass

        return " ".join((class_path, description))

    def _token_id_request(self, url, token_name_var = "subjectid",  **kwargs):
        kwargs[token_name_var] = self._token_id
        r = requests.get(url, params=kwargs)

        if r.status_code == requests.status_codes.codes.unauthorized:
            raise ClientUnauthorized()
        elif r.status_code != requests.status_codes.codes.ok:
            error_messages = self._parse_invalid_request(r.text)
            raise ClientException(r.status_code, error_messages)
        return r

    def validate_token(self):
        """
        Return if current token_id is still valid
        """
        r = requests.get(urljoin(self._url, Client._token_resource),
                         params={"tokenid": self._token_id})

        if r.status_code == requests.status_codes.codes.unauthorized:
            raise ClientUnauthorized()
        elif r.status_code != requests.status_codes.codes.ok:
            error_messages = self._parse_invalid_request(r.text)
            raise ClientException(r.status_code, error_messages)

        try:
            type_, value = r.text.split("=")
            value = value.strip(" \r\n")
        except Exception, e:
            raise ClientException(r.status_code,
                                  "Some error has ocurred getting the result value from %s"
                                  % r.text)

        return value == "true"

    def logout(self):
        """
        Logout client and expire current client session/token
        """
        kwargs = {}
        r = self._token_id_request(urljoin(self._url, Client._logout_resource), **kwargs)

    def attributes(self, *args):
        """
        Get a set of atributes, use **args to get just a sub set of atributes
        >> client.attributes("mail")
        {'mail': 'foo@bar.com'}
        """
        kwargs = {}
        if args:
            kwargs["attributenames"] = args

        r = self._token_id_request(urljoin(self._url, Client._attribute_resource), **kwargs)

        # parse contennt looking for all attributes
        attributes = []
        for line in r.text.splitlines():
            r = re.match("(userdetails\.attribute\.name)=(.*)", line)
            if r:
                name = r.groups()[1]
                attributes.append([name, None])
                continue  # next line

            r = re.match("(userdetails\.attribute\.value)=(.*)", line)
            if r:
                value = r.groups()[1]
                # last name parsed is where it has to
                # be stacked
                if attributes[-1][1] == None:
                    attributes[-1][1] = value
                if isinstance(attributes[-1][1], list):
                    attributes[-1][1].append(value)
                else:
                    # cast to list
                    attributes[-1].append([attributes[-1][1], value])

        return dict([(item[0], item[1]) for item in attributes])

    def set_attribute(self, name, value):
        """
        Set one atributes
        >> client.set_attribute("mail", "foo@gmail.com")
        True
        """
        kwargs = {"identity_name": self._username,
                  "identity_attribute_names": name,
                  "identity_attribute_values_%s" % name: value }

        try:
            r = self._token_id_request(urljoin(self._url, Client._set_attribute_resource),
                                       token_name_var="admin",
                                       **kwargs)
        except ClientException, c:
            if r.status_code == requests.status_codes.codes.server_error:
                # we dont have any way to know what has rised this error
                # we assume that this attribute doesn't exist
                return False
            raise c

        return True
