# Cracking the Smart Card puzzle

## Resources

- MSDN Blog [How to read a certificate from a smart card and...](https://blogs.msdn.microsoft.com/winsdk/2010/05/28/how-to-read-a-certificate-from-a-smart-card-and-add-it-to-the-system-store/)
- Chromium appears to be written in Python, and to use ctypes as well - [source code](https://chromium.googlesource.com/chromium/tools/depot_tools.git/+/master/fix_encoding.py)
- Specification - NIST SP 800-73, “Cryptographic Algorithms and Key Sizes for PIV.”

### The Python Part

- PyKCS11 needs to load the correct DLL or SO for the SmartCard vendor (ActivClient)
    - Windows - C:\Program Files\HID Global\ActivClient\acpkcs211.dll
    - Mac - /Library/Frameworks/ac.ac4mac.pkcs11.framework/Versions/Current/Libraries/acpkcs220.dylib

```python
from asn1crypto import x509
from PyKCS11 import *
pkcs11 = PyKCS11Lib()
pkcs11.load('C:\\Program Files\\HID Global\\ActivClient\\acpkcs211.dll')
session = pkcs11.openSession(slot, CKF_SERIAL_SESSION | CKF_RW_SESSION)
pkcs11.getSlotList(tokenPresent=False)
slot = pkcs11.getSlotList(tokenPresent=False)[0]
session = pkcs11.openSession(slot, CKF_SERIAL_SESSION | CKF_RW_SESSION)

# Here is where I enter the PIV code:
session.login('999999')

# Now enumerate the certificates and convert
result = []
certs = session.findObjects([(CKA_CLASS, CKO_CERTIFICATE)])
certs
len(certs)
result = []
for cert in certs:
    cka_value, cka_id = session.getAttributeValue(cert, [CKA_VALUE, CKA_ID])
    cert_der = bytes(cka_value)
    cert = x509.Certificate.load(cert_der)
    result.append(cert)
print(result)
result[0]
print(result[0].subject.contents)
```

### The Web Part

- Go to auth.nih.gov or authtest.nih.gov normally
- When we choose PIV, we are redirected - https://pivauthtest.nih.gov/CertAuthV2/forms/NIHPIVRedirector.aspx?TARGET=-SM-HTTPS%3a%2f%2fauthtest.nih.gov%2faffwebservices%2fredirectjsp%2fSAML2redirect.jsp%3fSPID%3durn%3aamazon%3awebservices%26appname%3dNLM%26SMPORTALURL%3dhttps-%3a-%2f-%2fauthtest.nih.gov-%2faffwebservices-%2fpublic-%2fsaml2sso%26SAMLTRANSACTIONID%3d17290830--29bb70bf--1d22e666--2c12087b--8cf8a8dc--fee
  This returns HTML, so the response document should be findable via Fiddler.
- Whatever is done locally, there is a GET to https://authtest.nih.gov/affwebservices/public/saml2sso?SMASSERTIONREF=QUERY&SPID=urn%3Aamazon%3Awebservices&appname=NLM&SAMLTRANSACTIONID=17290830-29bb70bf-1d22e666-2c12087b-8cf8a8dc-fee
- There are also lots of redirects

- When the user presses the "Log in" button, the following code is called in the submitForm function:

```javascript
window.location.href='https://pivauth.nih.gov/CertAuthV2/forms/HHSPIVRedirector.aspx?TARGET='+document.frm1.TARGET.value;
return false;
```

- It is important here to note that this code is a mess, because the setting of the href should cause page reload
  and nothing else should run after that. 
- HHSPIVRedirector.aspx does in fact redirect, but we cannot get that page using curl or Telerik Fiddler. Even if we
  did, we might see that it is running a custom version ActiveX control.  What we can tell is that the redirect page
  forces the prompt and then redirects back to HHSPIVRedirector.aspx.
- So, we can introspect the differences to the page content, cookies, and Query parameters between the initial load and
  the redirect back to HHSPIVRedirector.aspx

- It is probably just requiring a specific client certificate, so Windows puts up the dialog, and then when the client
  certificate is validated, it redirects both.
  
## Proving it works (together)

Try the below two ways:
 - Once with urllib and no urllib3, where the challenge will be cookie management and basic coding, but where we
   get OS certificate handling closer to vanilla.
 - Once with requests and urllib3, where the challenge will be creating a context dependent SSL adapter (e.g. that
   depends on the request).

Algorithm:
- Write script to go to https://authtest.nih.gov/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM
- Extract TARGET parameter from reponse
- For PIV login, then go to 'https://pivauth.nih.gov/CertAuthV2/forms/HHSPIVRedirector.aspx?TARGET=' + encoded(TARGET)
- If using requests, we may need to do this with redirect following off and use a different HTTPAdapter when the
  the URL path endswith('/smgetcred.scc'), or better yet, retry with the PIV x509 certificate pair whenever we get
  an SSL error (much more flexible, but raises eyebrows).
  
- At a lower level, this migth look like this:

```python
import requests
from bs4 import BeautifulSoup
from requests_toolbelt.adapters.x509 import X509Adapter

AUTH_URL = 'https://authtest.nih.gov/affwebservices/public/saml2sso?SPID=urn:amazon:webservices&appname=NLM'
PIV_URL = 'https://pivauth.nih.gov/CertAuthV2/forms/HHSPIVRedirector.aspx'

session = requests.Session()
r = session.get(AUTH_URL)
soup = BeautifulSoup(r.content, 'lxml')
target_value = soup.find('input', attrs={'name': 'target'}).get('value')
piv_url = PIV_URL + '?TARGET=' + target_value
r = session.get(piv_url, allow_redirects=False)
getcred_url = r.headers['Location']

# Load special adapter performing SSL encryption using a specific X509 certificate
session.mount('https://', X509Adapter(cert_bytes, private_key_bytes))
r = session.get(getcred_url, allow_redirects=False)
piv_url = r.headers['Location']

# Go back to "normal" adapter
session.mount('https://'. HTTPAdapter())
```

Problem here is that we've solved the part where we read the certificate using the PIV, but the private key lives
on the smart card and never leaves it.  We must implement the SSL ourselves, using primitives such as as:

 - RSA sign (private key) and verify (public key) -  https://pkcs11wrap.sourceforge.io/api/samples.html#rsa-sign-verify
 - Encrypt (for public key) decrypt (with private key) - https://pkcs11wrap.sourceforge.io/api/samples.html#encrypt-and-decrypt
 
### Another layer of the onion

See https://github.com/pyca/pyopenssl/issues/847 where I attempt to grapple with this.
Best resolution would be a new module `requests-pkcs11` which puts `PyKCS11`, `pyopenssl` and `requests` together.

Another solution is to write a `requests-winhttp` which provides an adapter that
uses [WinHTTP](https://docs.microsoft.com/en-us/windows/win32/winhttp/winhttp-start-page) through ctypes or cffi.
This would be a potentially cleaner way to interface with smart cards as multiple vendors would be supported.  

### Winscard API

- [Online documentation](https://docs.microsoft.com/en-us/windows/win32/api/winscard/)
- Include Files
    * `C:\Program Files (x86)\Windows Kits\8.1\Include\um\winscard.h`
    * `C:\Program Files (x86)\Windows Kits\8.1\Include\um\scarderr.h`
- Libraries
    * `C:\Windows\System32\winscard.dll`
    * `C:\Windows\System32\scarddlg.dll` (for dialog functions)

### Crypto API

- [Online documentation](https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/)
- Include Files
    * `C:\Program Files (x86)\Windows Kits\8.1\Include\um\wincrypt.h`
- Libraries
    * `C:\Windows\System32\advapi32.dll`
    

## Smart Card Debugging

So, how do we see how this is done?  By using logs and event viewer:

* https://docs.microsoft.com/en-us/windows/security/identity-protection/smart-cards/smart-card-debugging-information#debugging-and-tracing-using-wpp
* https://docs.microsoft.com/en-us/windows/win32/wmisdk/tracing-wmi-activity
* https://docs.microsoft.com/en-us/previous-versions//aa385225(v=vs.85)?redirectedfrom=MSDN

Here we reproduce some of the key commands that may be useful without installing the Windows Device driver Kit (WDK):

### Logging Parameters


| Friendly Name | GUID                                 | Flags  |
| ------------- | ------------------------------------ | ------ |
| scardsvr      | 13038e47-ffec-425d-bc69-5707708075fe | 0xffff | 
| winscard      | 3fce7c5f-fb3b-4bce-a9d8-55cc0ce1cf01 | 0xffff |
| basecsp       | 133a980d-035d-4e2d-b250-94577ad8fced |    0x7 |
| scksp         | 133a980d-035d-4e2d-b250-94577ad8fced |    0x7 |
| msclmd        | fb36caf4-582b-4604-8841-9263574c4f2c |    0x7 | 
| credprov      | dba0e0e0-505a-4ab6-aa3f-22f6f743b480 | 0xffff |
| certprop      | 30eae751-411f-414c-988b-a8bfa8913f49 | 0xffff |
| scfilter      | eed7f3c9-62ba-400e-a001-658869df9a91 | 0xffff |
| wudfusbccid   | a3c09ba3-2f62-4be5-a50f-8278a646ac9d | 0xffff | 

### Start Logging

Generic:

	logman start <FriendlyName> -ets -p {<GUID>} <Flags> -ft 1 -rt -o .\<LogFileName>.etl -mode 0x00080000

Specific:

	logman start scardsvr -ets -p {13038e47-ffec-425d-bc69-5707708075fe} 0xffff -ft 1 -rt -o .\scardsvr.etl -mode 0x00080000

### Stop Logging

Generic:

	logman -stop <FriendlyName> -ets

Specific:

	logman -stop scardsvr -ets

### View Log

* Start Event Viewer as administrator
* Choose menu item for View > Show Analytic and Debug Logs
* Navigate on the left to "Applications and Service Logs"
* Drill down to "Applications and Service Logs > Microsoft > Windows > WMI Activity"
* Right-click the "Trace" log and select "Open"
* Open the file you have obtained from tracing
