---
title: nlmfedcred / Configuration
---

## Path

On Windows, the `getawscreds` command-line looks first in `%APPDATA%\getawscreds.ini`, and then 
at `%USERPROFILE%\.getawscreds`. On Linux and MacOX, the only location checked is `~/.getawscreds`.

## Purpose of Configuration

The configuration is meant only to define the options that correspond
to [Named Profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html).

Sections of the configuration file define options for a specific
named profile, and the command-line typically saves the credentials to that named profile.

## Default Options

The defaults that apply to all named profiles are in a section
called "[DEFAULT]". For example, to set the default
role within AWS to one named "nlm_aws_users", you would write:

```ini
[DEFAULT]
role = nlm_aws_users
```

## Profile Specific Options

Roles such as "devel" or "prod" might be specified as below.

```ini
[devel]
idp = authtest.nih.gov
account = 999999999900
duration = 14400
role = myapp_poweruser_role

[prod]
idp = auth.nih.gov
account = 999999999901
role = myapp_user_role
```

__NOTE:__ These are not AWS account numbers or roles.

## Supported Options

Each section within the configuration file supports these
configurable parameters. These are also available on the command-line.


| Option   | Description |
|----------|-------------|
| idp      | Which federated server to use for authentication. This can optionally be a full url |
| account  | The AWS account number |  
| role     | The role within AWS - may be an ARN or a name |
| duration | Controls the requested duration for the temporary credentials |
| subject  | Controls which smartcard certificate will be used when authenticating by PIV |
| username | Allows a user to authenticate with a different username, for example a Service Account |

&nbsp;

## Setting the IDP (Identity Provider)

The IDP has a default, and typical values. Through substitution, "authexample.nih.gov" would become the following:

```
https://authexample.nih.gov/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM
```

You can optionally set the idp to the full URL as well in case you need to test
something unusual.