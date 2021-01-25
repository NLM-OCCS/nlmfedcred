---
title: nlmfedcred / How To
---

## Typical Usage with a Profile

Once the configuration file has been setup, the typical usage
is to authenticate the current user to a named profile:

```bash
getawscreds -p prod
```

This will lookup the profile section called "[prod]" or fallback to
the section called "[DEFAULT]", prompt the user for a password, submit the form,
obtain credentials from AWS, and then write these to the AWS
credentials file.

Then, you can use the AWS CLI with that profile:

```bash
aws ec2 describe-regions --profile prod
```

## What if I do not want to type --profile?

If you define the environment variable "AWS_PROFILE", the aws
command-line will honor it, and you can omit the argument to getawscreds:

```bash
getawscreds -p
```

## What roles are available to me?

Simply run getawscreds without arguments:

```bash
getawscreds
```

Typical output after you enter your password would be something like this:

```
Multiple potential roles found. Use --account or --role argument to limit to one.

Available roles below:
  arn:aws:iam::999999999900:role/myapp_user_role
  arn:aws:iam::999999999900:role/myapp_power_role
  arn:aws:iam::999999999901:role/myorg_user_role
  arn:aws:iam::999999999902:role/myorg_user_role
  arn:aws:iam::999999999903:role/myorg_user_role
  arn:aws:iam::999999999904:role/myorg_user_role
  arn:aws:iam::999999999905:role/myorg_user_role
  arn:aws:iam::999999999906:role/myorg_user_role
```

__NOTE:__ These are not real AWS role ARNs.

## How do I get credentials without saving them

With a service account you can use the "--shell"
console parameter along with a password:

```
getawscreds -p int --shell bash --password XXXXXXXXXXXXXXXX
```

This is not secure or really cloud-native, but it could
be needed while you are getting started.

You can also get output appropriate for the Windows
command prompt:

```
getawscreds -p int --shell cmd
```

## How can I authenticate with my PIV?

You need to tell getawscreds which certificate to use by 
configuring the "subject" parameter in the configuration.

Here's an example:

```ini
[DEFAULT]
subject = Daniel A. Davis -A (Affiliate)
idp = authexample.nih.gov

[devel]
account = 999999999901
role = myapp_user_role
```

Now, I can authenticate as follows:

```bash
getawscreds -p devel --piv
```

If you just logged in or authenticated to a website, you may
not be prompted for your PIV at all.

__Note__: This feature only supports Windows 10, and is pretty new.