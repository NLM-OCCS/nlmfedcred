# NLM Federated AWS Credentials

## Summary

Allows a command-line user to get temporarily credentials using their NIH Login

## Installation

This is normally installed from a python package repository, or from a built wheel file:

    pip install nlmfedcred

## Usage

This installs some Python libraries and a command, `getawscreds`.
Typically, users just run `getawscreds`.

### Windows CMD prompt

Typical usage is to direct the credentials to an output file, and then
source or execute the file:

    getawscreds -o awscreds.bat
    awscreds.bat

### Bash (Linux and MSYS supported)

Direct the output to a file and then source it:

    getawscreds -o awscreds.sh
    . awscreds.sh

### Accounts and Roles

The program will prompt you for what role to use, but you typically already know:

* Use the `--account` or `-a` argument to filter available roles by account.
* Use the `--role` or `-r` argument to filter available roles by role name.

Here's an example:

    getawscreds -o awscreds.sh -a 491634416615 -r nlm_aws_users

Here, the user is requesting a particular account number (NLM-QA) and a particular role.


### SSL Interceptor

Some of our systems sit behind a firewall/web proxy that acts as an SSL interceptor.   This allows it to decript the SSL traffic from an upstream web site, such as https://aws.amazon.com/, and analyze whether the content may be harmful.   However, the SSL interceptor then re-encrypts the content with its own certificate.  Python itself uses the Windows system certificates, which are stored in the registry, but libraries such as requests and urllib3 typically use certificates from the certifi python package.

The following command-line builds a multi-certificate PEM file appending our own SSL interceptor pem certificate to the PEM bundle distributed by the certifi package, and stores it in a location of your choosing, I use the path %APPDATA%\awscerts.pem as an example:

    getawscreds --setupcerts %APPDATA%\aws-certs-bundle.pem


There after, you can use this bundle with both getawscreds and with the aws command-line itself:

    getawscreds --cacerts %APPDATA%\aws-certs-bundle.pem -o awscreds.bat
    awscreds.bat
    aws --ca-bundle %APPDATA%\aws-certs-bundle.pem ec2 describe-region

### Configuration file and Profiles

The program looks for an INI file called `$HOME/.getawscreds`, or if you are used to Windows environment variables, `%USERPROFILE%\\.getawscreds`.  This file allows a user to provide values for the following command-line options:

    username
    cacerts
    account
    role
    idp

The defaults go in a seciton called `[DEFAULTS]`, and each additional section becomes a named profile you can use with the `--profile` or `-p` command-line flag.   The configuration file is typically used to provide names and federated login points for different accounts, but can also be used to provide specific roles.   A typical configuration for NLM's own environment is as follows:

    [DEFAULT]
    role = nlm_aws_users

    [NLM-INT]
    idp = authtest.nih.gov
    account = 758297805533

    [NLM-WG]
    idp = authtest.nih.gov
    account = 765460880451

    [NLM-PROD]
    idp = auth.nih.gov
    account = 070163433501

    [NLM-QA]
    idp = auth.nih.gov
    account = 491634416615

    [NLM-SEC]
    idp = auth.nih.gov
    account = 867452570402

### Region

You can change the region using the `--region` argument:

    getawscreds -o awscreds.sh --region us-west-1

### More Options

You can get usage in the tyical way:

    getawscreds -h

The following diagnostic flags exist:

* You can test that the shell output switching is working using the `--shell` argument.
* You can get a copy of the SAML Binding document returned by authtest.nih.gov using the `--samlout` argument.

## Development

- Building
    * Update the `VERSION.txt` and run `./setup.py bdist_wheel`
- Testing
    * Only manual at this point, I'm afraid

