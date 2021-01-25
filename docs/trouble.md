---
title: nlmfedcred / Trouble Shooting
---

This page provides trouble shooting procedures.

## Command Line Parameters

How can I find all the command line parameters:

```
getawscreds -h
```

## No SAML Binding

```
No SAML Binding: could it be an invalid password?
```

If it is not an invalid password, then your account may be locked.

## I got a RequestExpired error

I ran `getawscreds` and it seemed to work, but now I see something like:

```
An error occurred (RequestExpired) when ...
```

This means that the temporary credentials have expired.  However, it could
be for a different "Named Profile".  If you have multiple accounts and
roles, it can get quite confusing.   Quick trouble-shooting:

1. Check the AWS_PROFILE environment variable.
1. Check for a --profile parameter to the command.
1. See what getawscreds command you ran.

## What was the SAML assertion?

If something still is confusing, it is a good idea to verify
that you are getting a SAML assertion, and to save it
for analysis.  You can do this using the command-line argument
"--samlout".  This sets the path to be used to save the SAML 
assertion:

```
getawscreds --samlout saml_assertion.xml
```

The assertion is saved in an XML format.

You still will need to authenticate with the username and password
to save it.  The SAML assertion depends only on the idp and
username - might be useful for a new service account, or one
just moving from Development and integration to later stages:

```
getawscreds --username ServiceAccount --idp authexample.nih.gov --samlout service-saml.xml
```

### I tried to extend the duration

I put `duration = 14400` in my configuration file, and now I 
cannot authenticate.  

The duration must be configured both by the CIT NIH Login team, in your
AWS role, and then in the getawscreds command-line.  Try to 
login to the AWS Console in your browser and literally check
the maximum duration in the IAM > Roles area of the console.
