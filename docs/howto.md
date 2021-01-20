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
  arn:aws:iam::232258963078:role/nlm_aws_users
  arn:aws:iam::232258963078:role/nlm_aws_ab_django_user
  arn:aws:iam::758297805533:role/nlm_aws_users
  arn:aws:iam::204225352087:role/nlm_aws_users
  arn:aws:iam::272956248402:role/nlm_aws_users
  arn:aws:iam::626642342379:role/nlm_aws_users
  arn:aws:iam::976194488961:role/nlm_aws_users
  arn:aws:iam::740347601350:role/nlm_aws_users
```

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
idp = authtest.nih.gov

[default]
account = 232258963078
role = nlm_aws_users
```

Now, I can authenticate as follows:

```bash
getawscreds -p --piv
```

If you just logged in or authenticated to a website, you may
not be prompted at all.

__Note__: This feature only supports Windows 10, and is pretty new.