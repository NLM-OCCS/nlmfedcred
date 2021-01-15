---
title: nlmfedcred / About
---

This module provides a command-line `getawscreds` that allows a user to assume a role in an AWS account based 
on their NIH Login account. On Windows, users can use their PIV card or password, but on other platforms, users
must use their username and password.  Service accounts also use a username and password.

## How it works

The software requests your password or PIV PIN code, and then logs into
NIH login using these parameters.  When NIH login returns the SAML Assertion,
the software extracts it from the HTML page, and presents that XML (the SAML assertion)
directly to the AWS API 
[sts:AssumeRoleWithSAML](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithSAML.html).

That API returns credentials that are written into the AWS CLI credential file `~/.aws/credentials`, or output in a
format appropriate for a bash shell or for Windows command-prompt (`cmd.exe`).

## Named Profiles

An administrator or developer may be granted through the SAML assertion the ability
to authenticate to multiple roles on multiple accounts in AWS. Luckily, the AWS CLI and libraries support a concept
called [Named Profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) 
so that a user can manage the credentials for many profiles.

In order to know which federated role corresponds to which profile in which AWS
account, the `getawscreds` command-line read a configuration file.

## Working with IDEs

Since the temporary credentials are written into the standard AWS
credentials file, `~/.aws/credentials`, working with an IDE is usually
as simple as specifying which Profile should be used.
