
from bs4 import BeautifulSoup
from six.moves.urllib.parse import quote_plus, urlsplit, urlunsplit

import pythoncom
import win32com.client

# We pretend to be Chrome 79 just to make sure
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'


def win32_get(session, url, cert=None):
    session.Open('GET', url)
    session.SetRequestHeader('User-Agent', USER_AGENT)
    if cert:
        session.SetClientCertificate(cert)
    session.Send()
    if session.Status != 200:
        raise Exception('Network Protocol Error - %s' % session.StatusText)
    return session.ResponseText


def find_target(soup):
    target_input = soup.find('input', attrs={'name': 'TARGET'})
    if not target_input:
        target_input = soup.find('input', attrs={'name': 'target'})
    return target_input.get('value') if target_input else None


def process_redirector_target(target):
    if target.startswith('-SM-'):
        target = target[4:]
    if target.startswith('HTTPS:'):
        target = 'https:' + target[6:]
    target = target.replace('-:', ':')
    target = target.replace('-/', '/')
    target = target.replace('-=', '=')
    target = target.replace('-%', '%')
    target = target.replace('-?', '?')
    target = target.replace('-;', ';')
    target = target.replace('-+', '+')
    target = target.replace('-#', '#')
    target = target.replace('-&', '&')
    target = target.replace('- ', ' ')
    target = target.replace('-_', '_')
    target = target.replace('-.', '.')
    target = target.replace('-@', '@')
    target = target.replace('--', '-')

    split = urlsplit(target)
    query = split.query
    params = dict(p.split('=', 1) for p in query.split('&'))
    params['SPID'] = quote_plus(params['SPID'])
    params['SMPORTALURL'] = quote_plus(params['SMPORTALURL'])
    query = '&'.join(k + '=' + v for k, v in params.items())
    target = urlunsplit((split.scheme, split.netloc, split.path, query, split.fragment))
    return target


def get_saml_assertion_piv(subject, idp, session=None):
    if session is None:
        pythoncom.CoInitialize()
        session = win32com.client.Dispatch('WinHttp.WinHttpRequest.5.1')

    body = win32_get(session, idp.form_url)
    soup = BeautifulSoup(body, 'lxml')
    target = find_target(soup)

    cert = 'CURRENT_USER\\MY\\' + subject
    piv_url = idp.piv_url + '?TARGET=' + target
    body = win32_get(session, piv_url, cert=cert)
    soup = BeautifulSoup(body, 'lxml')
    target = find_target(soup)

    url = process_redirector_target(target)
    body = win32_get(session, url)
    soup = BeautifulSoup(body, 'lxml')
    samlinput = soup.find('input')

    assert samlinput
    samlvalue = samlinput.attrs['value']
    return samlvalue
