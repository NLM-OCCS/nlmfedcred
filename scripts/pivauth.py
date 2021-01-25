import sys
from argparse import ArgumentParser
from http.cookiejar import CookieJar
from urllib.request import HTTPCookieProcessor, build_opener

from bs4 import BeautifulSoup

AUTH_URL = 'https://authtest.nih.gov/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM'
PIV_URL = 'https://pivauth.nih.gov/CertAuthV2/forms/HHSPIVRedirector.aspx'


def create_parser(prog_name):
    parser = ArgumentParser(prog=prog_name)
    parser.add_argument('--auth',  metavar='URL', default=AUTH_URL,
                        help='initial auth URL, default %s' % AUTH_URL)
    parser.add_argument('--piv', metavar='URL', default=PIV_URL,
                        help='redirector URL, default %s' % PIV_URL)
    return parser


def parse_args(prog_name, args):
    parser = create_parser(prog_name)
    return parser.parse_args(args)


def get_target(url, opener):
    with opener.open(url) as response:
        if response.getcode() != 200:
            raise Exception('Network Protocol Error')
        body_bytes = response.read()
        soup = BeautifulSoup(body_bytes, 'lxml')
        target_input = soup.find('input', attrs={'name': 'TARGET'})
        if not target_input:
            target_input = soup.find('input', attrs={'name': 'target'})
        return target_input.get('value') if target_input else None


def main():
    opts = parse_args(sys.argv[0], sys.argv[1:])
    opener = build_opener(HTTPCookieProcessor())
    target_value = get_target(opts.auth, opener)
    piv_url = opts.piv + '?TARGET=' + target_value
    with opener.open(piv_url) as response:
        if response.getcode() != 200:
            raise Exception('Network Protocol Error')
        body_bytes = response.read()
        sys.stdout.write(body_bytes)


if __name__ == '__main__':
    main()
