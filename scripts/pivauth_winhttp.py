import sys
from argparse import ArgumentParser

from bs4 import BeautifulSoup
import pythoncom
import win32com.client

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


def get_target(url, winRequest):
    winRequest.Open('GET', url)
    winRequest.Send()

    if winRequest.Status != 200:
        raise Exception('Network Protocol Error')
    body  = winRequest.ResponseText
    soup = BeautifulSoup(body, 'lxml')
    target_input = soup.find('input', attrs={'name': 'TARGET'})
    if not target_input:
        target_input = soup.find('input', attrs={'name': 'target'})
    return target_input.get('value') if target_input else None


def get_piv(url, winRequest):
    winRequest.Open('GET', url)
    winRequest.SetClientCertificate('path to a certificate in the registry')
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
    get_piv(piv_url, winRequest)


if __name__ == '__main__':
    main()
