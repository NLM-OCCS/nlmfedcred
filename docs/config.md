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
called "[DEFAULT]" so as to avoid conflicting with the AWS
named profile called "default".  For example, to set the default
role within AWS to one named "nlm_aws_users", you would write:

```ini
[DEFAULT]
role = nlm_aws_users
```

## Profile Specific Options

Roles such as "default", "prod", and "devel" might be specified as follows:

```ini
[default]
idp = authtest.nih.gov
account = 758297805533
role = nlm_aws_users

[devel]
idp = authtest.nih.gov
account = 232258963078
duration = 14400
role = nlm_aws_myapp_user

[prod]
idp = auth.nih.gov
account = 070163433501
role = nlm_aws_users
```

## Supported Options

Each section within the configuration file supports these
configurable parameters. These are also available on the command-line.


| Option   | Description |
|----------|-------------|
| idp      | Which federated server to use for authentication | 
| account  | The AWS account number |  
| role     | The role within AWS - may be an ARN or a name |
| duration | Controls the requested duration for the temporary credentials |
| subject  | Controls which smartcard certificate will be used when authenticating by PIV |
| username | Allows a user to authenticate with a different username, for example a Service Account |


