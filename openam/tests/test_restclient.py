#  Pau Freixes, pfreixes@gmail.com
#  2013-08

import unittest

from mock import patch
from StringIO import StringIO
from openam import restclient
from requests import Response, status_codes


class RestClientTestCase(unittest.TestCase):

    def setUp(self):
        self.username = "demo"
        self.password = "demopass"
        self.url = "http://localhost:8080/openam"
        self.token_id = "AQIC5wM2LY4SfczncpY2PEufFAyRqXP2oW_Qkb_g80AgNOw.*AAJTS" +\
                        "QACMDEAAlNLABM0Mjk0NDEwMjA5asdfMzM1NjY3NTUy*"

    def _build_response(self, status_code, body, headers={}):
        r = Response()
        r.status_code = status_code
        r.raw = StringIO(body)
        r.url = r.request = r.connection = None  # not necessary
        return r

    def _get_authenticated_instance(self, MockGet):
        MockGet.return_value = self._build_response(status_codes.codes.ok,
                                                    "token_id=%s" % self.token_id)
        c = restclient.Client(self.url, self.username, self.password)
        return c

    @patch("requests.get")
    def test_authentication_failed(self, MockGet):
        MockGet.return_value = self._build_response(status_codes.codes.unauthorized, "")
        self.assertRaises(restclient.ClientAuthenticationFailed,
                          restclient.Client,
                          self.url, self.username, "asdfasdf")
        MockGet.assert_called_once_with(self.url + restclient.Client._auth_resource,
                                        params={"username": self.username, "password": "asdfasdf"})

    @patch("requests.get")
    def test_authentication(self, MockGet):
        c = self._get_authenticated_instance(MockGet)
        MockGet.assert_called_once_with(self.url + restclient.Client._auth_resource,
                                        params={"username": self.username,
                                        "password": self.password})
        self.assertEqual(c.token_id, self.token_id)
        self.assertEqual(c.username, self.username)

    @patch("requests.get")
    def test_logout(self, MockGet):
        c = self._get_authenticated_instance(MockGet)
        MockGet.return_value = self._build_response(status_codes.codes.ok, "")
        c.logout()
        MockGet.assert_called_with(self.url + restclient.Client._logout_resource,
                                   params={"subjectid": self.token_id})

    @patch("requests.get")
    def test_valid_token(self, MockGet):
        c = self._get_authenticated_instance(MockGet)
        MockGet.return_value = self._build_response(status_codes.codes.ok, "bool=true")
        self.assertEquals(c.validate_token(), True)
        MockGet.assert_called_with(self.url + restclient.Client._token_resource,
                                   params={"tokenid": self.token_id})

    @patch("requests.get")
    def test_attributes(self, MockGet):
        c = self._get_authenticated_instance(MockGet)
        body = ("userdetails.token.id=%s\n" % self.token_id) +\
            "userdetails.attribute.name=uid\n" +\
            "userdetails.attribute.value=demo\n" +\
            "userdetails.attribute.name=mail\n" +\
            "userdetails.attribute.value=demo@demo.com\n" +\
            "userdetails.attribute.name=sn\n" +\
            "userdetails.attribute.value=demo\n" +\
            "userdetails.attribute.name=userpassword\n" +\
            "userdetails.attribute.value={SSHA}N4GXaQsYDHii/pCcF5Q3nWt/bp/qC5Hnw2LKKQ==\n" +\
            "userdetails.attribute.name=cn\n" +\
            "userdetails.attribute.value=demo\n" +\
            "userdetails.attribute.name=inetuserstatus\n" +\
            "userdetails.attribute.value=Active\n" +\
            "userdetails.attribute.name=dn\n" +\
            "userdetails.attribute.value=uid=demo,ou=people,dc=openam,dc=forgerock,dc=org\n" +\
            "userdetails.attribute.name=objectclass\n" +\
            "userdetails.attribute.value=person\n" +\
            "userdetails.attribute.value=sunIdentityServerLibertyPPService\n" +\
            "userdetails.attribute.value=inetorgperson\n"
        MockGet.return_value = self._build_response(status_codes.codes.ok, body)
        attr = c.attributes()
        #check a sub set ... lazy moment
        self.assertEqual(attr["uid"], "demo")
        self.assertEqual(attr["mail"], "demo@demo.com")
        MockGet.assert_called_with(self.url + restclient.Client._attribute_resource,
                                   params={"subjectid": self.token_id})

    @patch("requests.get")
    def test_set_attribute(self, MockGet):
        c = self._get_authenticated_instance(MockGet)
        MockGet.return_value = self._build_response(status_codes.codes.ok, "")
        attr = c.set_attribute("mail", "foo@example.com")
        params = {"identity_name": self.username,
                  "identity_attribute_names": "mail",
                  "identity_attribute_values_mail": "foo@example.com"}
        params["admin"] = self.token_id
        MockGet.assert_called_with(self.url + restclient.Client._set_attribute_resource,
                                   params=params)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RestClientTestCase, 'test'))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
