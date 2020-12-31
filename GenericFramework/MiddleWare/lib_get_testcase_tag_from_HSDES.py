"""
As HSDES is an internal server, this feature will not open source.
Performs to get test case field value(eg:tag, title) form HSDES server.
Title      	: lib_get_testcase_tag_from_HSDES.py
Author(s)  	: Liang Yan
Description	: Things to perform:
            1. Get the test case field value by given test case id.
"""
import os
import urllib3
import traceback
import requests
from requests_kerberos import HTTPKerberosAuth
from SoftwareAbstractionLayer import lib_parse_config


class HSDES(object):
    """
    Support get test case field value from HSDES.

    """
    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.HSDES_URL = r'https://hsdes-api.intel.com/rest/auth/'
        self.headers = {'Content-type': 'application/json'}
        self.auth = self.get_auth()

    def get_auth(self):
        """
        Function Name       : get_auth
        Parameters          : None
        Functionality       : Get the auth value, provide 2 solution for auth.
                                1. Access HSDES server by providing username/token setting in system_configuration.ini.
                                   get token from https://servicetokens.intel.com, SPI: 4C18251A.
                                   a token Valid for 90 days, renew after token expiration.
                                2. if host machine login with the domain account, and this account got permission to
                                   access HSDES, no need to provide any parameter in system_configuration.ini.
                                   This solution only support for windows OS.
                              Once config username/token in system_configuration.ini, it will go through solution 1.
                              otherwise go through solution 2.

        Function Invoked    : None
        Return Value        : auth type
        """
        try:
            SUT_CONFIG_CLIENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir,
                                              r"SoftwareAbstractionLayer\system_configuration.ini")
            config = lib_parse_config.ParseConfig()
            username = config.get_value(SUT_CONFIG_CLIENTS, 'HSDES', 'username')
            token = config.get_value(SUT_CONFIG_CLIENTS, 'HSDES', 'token')
        except lib_parse_config.ParseConfigError:
            self.HSDES_URL = r'https://hsdes-api.intel.com/rest/'
            return HTTPKerberosAuth()
        return (username, token)

    def get_field(self, article_id, field=None):
        """
        Function Name       : get_field
        Parameters          :
                            article_id: the test case id
                            field: default value is None means get all the fields
                                   get one field by using str type such as 'title'
                                   get a list of field by using list type such as ['title', 'id', 'tag']
        Functionality       : get one test case field from HSDES server
        Function Invoked    : req
        Return Value        : a dict will return with containing all the field value, if getting value successfully,
                            dict format as below:
                            {
                                'data': [
                                    {
                                        'tag': '',
                                        'title': '',
                                        'id': ''
                                        .
                                        .
                                        .
                                    }
                                ]
                            }
                            else failed, dict format as below:
                            {
                                'errorCode': 'TIMEOUT'
                                'errorMessage': 'Timed out ..'
                                'debugContext': {
                                        'method': method,
                                        'url': url,
                                        'headers': options.get('headers', ''),
                                        'tb': traceback.format_exc()
                                    }
                            }
        """
        rest_api_article = self.HSDES_URL + 'article/'
        if field is None:
            url = '{}{}'.format(rest_api_article, article_id)
        elif isinstance(field, str):
            url = '{}{}?fields={}'.format(rest_api_article, article_id, field)
        elif isinstance(field, list):
            url = '{}{}?fields='.format(rest_api_article, article_id)
            for fld in field:
                if field.index(fld) == 0:
                    url = '{}{}'.format(url, fld)
                else:
                    url = '{}%2C{}'.format(url, fld)
        else:
            error_msg = 'bad operand type for {} _get_field'.format(self.__class__.__name__)
            raise TypeError(error_msg)
        return self.req('get', url, verify=False, auth=self.auth, headers=self.headers)

    @staticmethod
    def req(method, url, **options):
        """
        Function Name       : req
        Parameters          : method: 'get', 'post', 'put'.
                              url: HSDES rest address
                              **options: same as request
        Functionality       : basic function for request
        Function Invoked    :
        Return Value        : response from the HSDES server if success, else resp as below:
                             {
                                'errorCode': 'TIMEOUT'
                                'errorMessage': 'Timed out ..'
                                'debugContext': {
                                        'method': method,
                                        'url': url,
                                        'headers': options.get('headers', ''),
                                        'tb': traceback.format_exc()
                                    }
                            }
                                .
        """
        resp, response = None, None
        try:
            response = requests.request(method, url, **options)
            response.raise_for_status()
            resp = response.json()
        except requests.exceptions.Timeout as exception:
            resp = {"errorCode": "TIMEOUT",
                    "errorMessage": "Timed out {}".format(exception)}
        except requests.exceptions.ConnectionError as exception:
            resp = {"errorCode": "CONNECTION_ERROR",
                    "errorMessage": "Connection error {}".format(exception)}
        except requests.exceptions.HTTPError as exception:
            resp = {"errorCode": "HTTP_{status_code}_ERROR".format(status_code=exception.response.status_code),
                    "errorMessage": "Http error {}".format(exception)}
        except Exception as exception:
            resp = {"errorCode": "UNEXPECTED_ERROR",
                    "errorMessage": "Unexpected Error {}".format(exception)}

        # Gathering debugging context when an Error occurs
        if resp and "errorMessage" in resp:
            context = {
                'method': method,
                'url': url,
                'headers': options.get('headers', ''),
                # Getting detailed error
                'tb': traceback.format_exc()
            }
            # trying to get extra data about potential Response if any

            if response is not None and isinstance(response, requests.models.Response):
                try:
                    content = response.content
                except (requests.RequestException, RuntimeError) as error:
                    content = error.message

                # Getting all extra data from Response
                context['response'] = {
                    'links': response.links,
                    'reason': response.reason,
                    'elapsed': response.elapsed,
                    'content': content
                }
                resp['debugContext'] = context

        return resp


def test():
    """function for test this lib api"""
    hs = HSDES()
    result = hs.get_field(1608546012, 'title')
    if 'errorMessage' not in result:
        print(result['data'][0]['title'])
    else:
        print(result)


if __name__ == '__main__':
    test()
