import sys
from argparse import ArgumentParser
from urllib.parse import quote_plus, urlsplit, urlunsplit

from bs4 import BeautifulSoup
import pythoncom
import win32com.client

AUTH_URL = 'https://authtest.nih.gov/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM'
PIV_URL = 'https://pivauth.nih.gov/CertAuthV2/forms/HHSPIVRedirector.aspx'
REDIRECTOR_URL = 'https://pivauth.nih.gov/CertAuthV2/forms/HHSPIVRedirector.aspx'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'

def create_parser(prog_name):
    parser = ArgumentParser(prog=prog_name)
    parser.add_argument('--auth',  metavar='URL', default=AUTH_URL,
                        help='initial auth URL, default %s' % AUTH_URL)
    parser.add_argument('--cert', metavar='REGISTRY_KEY', default='CURRENT_USER\\MY\\Daniel A. Davis -A (Affiliate)',
                        help='Specify a registry path to a certificate')
    parser.add_argument('--piv', metavar='URL', default=PIV_URL,
                        help='redirector URL, default %s' % PIV_URL)
    return parser


def parse_args(prog_name, args):
    parser = create_parser(prog_name)
    return parser.parse_args(args)


def get_target(url, winRequest):
    winRequest.Open('GET', url)
    winRequest.SetRequestHeader('User-Agent', USER_AGENT)
    winRequest.Send()

    if winRequest.Status != 200:
        raise Exception('Network Protocol Error')
    body  = winRequest.ResponseText
    soup = BeautifulSoup(body, 'lxml')
    target_input = soup.find('input', attrs={'name': 'TARGET'})
    if not target_input:
        target_input = soup.find('input', attrs={'name': 'target'})
    return target_input.get('value') if target_input else None


def process_target(target):
    if target.startswith('-SM-'):
        target = target[4:]
    if target.startswith('HTTPS:'):
        target = 'https:'+target[6:]
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
    query = '&'.join(k+'='+v for k, v in params.items())
    target = urlunsplit((split.scheme, split.netloc, split.path, query, split.fragment))
    return target


def get_redirect_with_piv(url, winRequest, cert=None):
    winRequest.Open('GET', url)
    winRequest.SetRequestHeader('User-Agent', USER_AGENT)
    if cert:
        winRequest.SetClientCertificate(cert)
    winRequest.Send()

    if winRequest.Status != 200:
        raise Exception('Network Protocol Error - %s' % winRequest.StatusText)
    body  = winRequest.ResponseText
    soup = BeautifulSoup(body, 'lxml')
    target_input = soup.find('input', attrs={'name': 'TARGET'})
    if not target_input:
        target_input = soup.find('input', attrs={'name': 'target'})
    return target_input.get('value') if target_input else None


def post_target(url, winRequest):
    winRequest.Open('GET', url)
    winRequest.SetRequestHeader('User-Agent', USER_AGENT)
    winRequest.Send()
    if winRequest.Status != 200:
        raise Exception('Network Protocol Error - %s' % winRequest.StatusText)
    body  = winRequest.ResponseText
    sys.stdout.write(body)


def main():
    opts = parse_args(sys.argv[0], sys.argv[1:])

    pythoncom.CoInitialize()
    winRequest = win32com.client.Dispatch('WinHTTP.WinHTTPRequest.5.1')

    target_value = get_target(opts.auth, winRequest)

    piv_url = opts.piv + '?TARGET=' + target_value
    value = get_redirect_with_piv(piv_url, winRequest, opts.cert)
    value = process_target(value)
    print(value)
    post_target(value, winRequest)


if __name__ == '__main__':
    main()
