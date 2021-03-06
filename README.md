# NLM Federated AWS Credentials

## Summary

This module provides a command-line allowing NLM staff to obtain temporary credentials for AWS using NIH Login.

## Installation

This is normally installed from a python package repository, or from a built wheel file:

    pip install nlmfedcred

## Usage

This installs some Python libraries and a command, `getawscreds`.
Typically, users just run `getawscreds -p <profile>`.

See the documentation at https://nlm-occs.github.io/nlmfedcred/ for
more information.

### SSL Interceptor

Some of our systems sit behind a firewall/web proxy that acts as an SSL interceptor.   This allows it to decript the SSL traffic from an upstream web site, such as https://aws.amazon.com/, and analyze whether the content may be harmful.   However, the SSL interceptor then re-encrypts the content with its own certificate.  Python itself uses the Windows system certificates, which are stored in the registry, but libraries such as requests and urllib3 typically use certificates from the certifi python package.

The following command-line builds a multi-certificate PEM file appending our own SSL interceptor pem certificate to the PEM bundle distributed by the certifi package, and stores it in a location of your choosing, I use the path %APPDATA%\awscerts.pem as an example:

    getawscreds --setupcerts %APPDATA%\aws-certs-bundle.pem


There after, you can use this bundle with both getawscreds and with the aws command-line itself:

    getawscreds --cacerts %APPDATA%\aws-certs-bundle.pem -o awscreds.bat
    awscreds.bat
    aws --ca-bundle %APPDATA%\aws-certs-bundle.pem ec2 describe-region

### Configuration file and Profiles

The program looks for an INI file called `%APPDATA%\getawscreds.ini` or `$HOME/.getawscreds`:
On Windows, `%USERPROFILE%\.getawscreds` is still supported.

The defaults go in a section called `[DEFAULT]`, and each additional section becomes a named profile you can use with the `--profile` or `-p` command-line flag.   The configuration file is typically used to provide names and federated login points for different accounts, but can also be used to provide specific roles.   A typical configuration for NLM's own environment is as follows:

    [DEFAULT]
    role = myapp_user_role

    [int]
    idp = fubartest.nih.gov
    account = 999999999901

    [qa]
    idp = fubar.nih.gov
    account = 999999999902

    [prod]
    idp = fubar.nih.gov
    account = 999999999903

### Region

You can change the region using the `--region` argument:

    getawscreds -o awscreds.sh --region us-west-1

or with the environment variable `AWS_DEFAULT_REGION`.

### More Options

You can get usage in the typical way:

    getawscreds -h

The following diagnostic flags exist:

* You can test that the shell output switching is working using the `--shell` argument.
* You can get a copy of the SAML Binding document returned by authtest.nih.gov using the `--samlout` argument.

## Development

- Building
    * Update the `VERSION.txt` and run `./setup.py sdist bdist_wheel`
- Testing
    * Only manual at this point, I'm afraid:
    * `pytest`
    * `flake8`