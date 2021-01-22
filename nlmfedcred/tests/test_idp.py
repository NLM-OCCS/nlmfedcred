from nlmfedcred.idp import (DEFAULT_FORM_URL, DEFAULT_LOGIN_URL,
                            DEFAULT_PIV_URL, make_idp)


def test_defaults():
    assert 'authtest.nih.gov' in DEFAULT_FORM_URL
    assert 'authtest.nih.gov' in DEFAULT_LOGIN_URL
    assert 'authtest.nih.gov' in DEFAULT_PIV_URL


def test_make_idp():
    idp = make_idp('authfu.nih.gov')
    assert 'authfu.nih.gov' in idp.form_url
    assert 'authfu.nih.gov' in idp.login_url
    assert 'authfu.nih.gov' in idp.piv_url


def test_make_idp_from_url():
    form_url = 'https://authfu.nih.gov/affweb/public/saml2sso?SPID=urn:amazon:webservices&appname=NHLBI'
    idp = make_idp(form_url)
    assert idp.form_url == form_url
    assert 'authfu.nih.gov' in idp.login_url
    assert 'authfu.nih.gov' in idp.piv_url
