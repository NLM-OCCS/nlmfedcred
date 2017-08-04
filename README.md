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
