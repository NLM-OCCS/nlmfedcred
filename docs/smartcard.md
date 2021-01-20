---
title: nlmfedcred / Smart Card Utility
---

This page covers the Smart Card Utility which is an optional component.

## Installation

In addition the regular requirements, the utility requires
the optional package [PyKCS11](https://pypi.org/project/PyKCS11/).

This package is optional because it can be hard to build and is generally 
not required.  However, it can be useful when setting up PIV authentication on Windows, or
extracting the public key for an EC2 Key Pair.

## Prompting for the PIV PIN

The smart card will generally prompt you for the PIV PIN like this:

```
Enter PIN: 
```

The PIN is never stored except in the script's memory.

## Setup for using --piv

The most typical usage is to just fine exactly what you
should put into the configuration file to get it to work:

```
smartcard setup
```

This will print something like:

```
subject = Daniel A. Davis- A
```

That's what you put in the configuration file.  Note this must
match exactly.

## Listing Certificates

You can list all certificates on the smart card as follows:

```
smartcard certs
```

## Extracting a public key

You can extract a public key as follows:

```
smartcard pubkey
```

By default, this exports "slot 0" of the smart card.  You
can export a different slot as follows:

```
smartcard pubkey --cert 1
```

If for some reason you want this as a PEM file rather than
an OpenSSH key, use the option `--format pem`:

```
smartcard pubkey --format pem
```

If you want to save it to a file, give the `--key path` argument:

```
smartcard pubkey --key id_rsa_piv.pub
```

## Problems

### Incorrect PIN

It printed:

```
PyKCS11.PyKCS11Error: CKR_PIN_INCORRECT (0x000000A0)
```

This was an incorrect PIN - I don't want to make it too smart.

### It hangs

If you are on Mac, try pulling out the PIV card and replacing it.
Try again after replacing it.

### Other errors

Try a different card reader - this is based on opensource software
that may not work right with all card readers.  More likely
to work on Windows, actually.
