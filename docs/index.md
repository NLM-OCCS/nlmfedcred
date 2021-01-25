---
title: nlmfedcred / About
---

This module provides a command-line `getawscreds` that allows a user to assume a role in an AWS account based 
on their NIH Login account. On Windows, users can use their PIV card or password, but on other platforms, users
must use their username and password.  Service accounts also use a username and password.

## How it works

The software requests your password or PIV PIN code, and then logs into
NIH login using these parameters. NIH login returns HTML that encodes what
accounts and roles you may become, along with a web form that would automatically
submit to AWS.  This software extracts the information, called a SAML Assertion, and presents 
it directly to the AWS API 
[sts:AssumeRoleWithSAML](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoleWithSAML.html).

That API returns temporary credentials, typically good for about an hour.  The software
writes these into the AWS CLI credential file `~/.aws/credentials`, or outputs the credentials 
for a bash shell or for Windows command-prompt (`cmd.exe`).

## Named Profiles

A user may be granted the ability to authenticate to multiple roles on multiple accounts in AWS.
The information about which accounts and roles are available is encoded into
the SAML Assertion. Luckily, the AWS CLI and libraries support a concept
called [Named Profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) 
so that a user can manage the credentials for many profiles.

In order to know which federated role corresponds to which profile in which AWS
account, the `getawscreds` command-line read a configuration file.

## Typical Usage

Once a configuration file is created, typical usage is to type:

```bash
getawscreds -p profile --piv
```

or
 
```bash
getawscreds -p profile
```

You will then be prompted as needed.

## Working with IDEs

Since the temporary credentials are written into the standard AWS
credentials file, `~/.aws/credentials`, working with an IDE is usually
as simple as specifying which AWS profile should be used.
