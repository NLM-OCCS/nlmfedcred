from collections import namedtuple


FORM_URL_FORMAT = 'https://%s/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM'
LOGIN_URL_FORMAT = 'https://%s/siteminderagent/forms/login.fcc'

DEFAULT_IDP_FQDN = 'authtest.nih.gov'
DEFAULT_FORM_URL = FORM_URL_FORMAT % DEFAULT_IDP_FQDN
DEFAULT_LOGIN_URL = LOGIN_URL_FORMAT % DEFAULT_IDP_FQDN

# Create a namespace object with two fields
IDP = namedtuple('IDP', ('form_url', 'login_url',))

DEFAULT_IDP = IDP(DEFAULT_FORM_URL, DEFAULT_LOGIN_URL)


def make_idp(fqdn):
    return IDP(FORM_URL_FORMAT % fqdn, LOGIN_URL_FORMAT % fqdn)