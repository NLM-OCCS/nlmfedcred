from nlmfedcred.idp import (DEFAULT_FORM_URL, DEFAULT_LOGIN_URL,
                            DEFAULT_PIV_URL, make_idp)


def test_defaults():
    assert 'authtest.nih.gov' in DEFAULT_FORM_URL
    assert 'authtest.nih.gov' in DEFAULT_LOGIN_URL
    assert 'pivauthtest.nih.gov' in DEFAULT_PIV_URL


def test_make_idp():
    idp = make_idp('authfu.nih.gov')
    assert 'authfu.nih.gov' in idp.form_url
    assert 'authfu.nih.gov' in idp.login_url
    assert 'pivauthfu.nih.gov' in idp.piv_url
