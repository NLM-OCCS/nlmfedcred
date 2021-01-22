from collections import namedtuple
from urllib.parse import urlsplit, urlunsplit

FORM_URL_PATH = '/affwebservices/public/saml2sso'
FORM_URL_QUERY = 'SPID=urn:amazon:webservices&appname=NLM'
LOGIN_URL_FORMAT = 'https://%s/siteminderagent/forms/login.fcc'
PIV_URL_FORMAT = 'https://%s/CertAuthV3/forms/NIHPIVRedirector.aspx'
DEFAULT_IDP_FQDN = 'authtest.nih.gov'
DEFAULT_FORM_URL = 'https://%s%s?%s' % (DEFAULT_IDP_FQDN, FORM_URL_PATH, FORM_URL_QUERY)
DEFAULT_LOGIN_URL = LOGIN_URL_FORMAT % DEFAULT_IDP_FQDN
DEFAULT_PIV_URL = PIV_URL_FORMAT % DEFAULT_IDP_FQDN

# Create a namespace object with two fields
IDP = namedtuple('IDP', ('form_url', 'login_url', 'piv_url'))

DEFAULT_IDP = IDP(DEFAULT_FORM_URL, DEFAULT_LOGIN_URL, DEFAULT_PIV_URL)


def make_idp(fqdn):
    if fqdn.startswith('https'):
        url = urlsplit(fqdn)
        fqdn = url.netloc
        path = url.path if url.path else FORM_URL_PATH
        query = url.query if url.query else FORM_URL_QUERY
    else:
        path = FORM_URL_PATH
        query = FORM_URL_QUERY
    form_url = urlunsplit(['https', fqdn, path, query, ''])
    return IDP(form_url, LOGIN_URL_FORMAT % fqdn, PIV_URL_FORMAT % fqdn)
