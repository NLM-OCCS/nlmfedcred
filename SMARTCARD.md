# Smart Card Authentication

## Summary

SmartCard authentication is based on the server requesting SSL client authentication based on an X.509 certificate
which uses a private key that lives only on the smart card.  Our priority for SmartCard authentication
is Windows, and so we use Windows APIs to do the HTTP requests rather than the Python requests
library.  We do this by loading a Windows COM object, "WinHttp.WinHttpRequest.5.1".

The code is present in `nlmfedcred\fedcred_win32.py`. 

## Resources

- The topic [WinHTTP](https://docs.microsoft.com/en-us/windows/win32/winhttp/winhttp-start-page) has documentation
for WinHttpRequest.
- The topic [SSL in WinHTTP](https://docs.microsoft.com/en-us/windows/win32/winhttp/ssl-in-winhttp) defined how to load
a particular subject.

## Development Notes
 
### PyKCS11

Along the way to developing this code, we fouind PyKCS11 package which is able to perform SmartCard
encrytion/decryption at the Python level using ffi or ctypes Foreign-Function interface.

See `scripts\smartcard.py` for insight.  Note that PyKCS11 needs to load a
correct DLL or SO for the SmartCard.

### Registry

It may be necessary to interogate the Windows registry to see what authentication
certificates are present in the system and valid.  See `scripts\choosecert.py` for some
details on this.  The most useful function there is `store_search` which will return all
of the registry keys which may contain certificate values.

- The topic [System Store Locations](https://docs.microsoft.com/en-us/windows/win32/seccrypto/system-store-locations)
shows how certificate stores relate to registry keysv
- The blog entry [Extracting Certificates from the Windows Registry](https://blog.nviso.be/2019/08/28/extracting-certificates-from-the-windows-registry/)
illustrates how each registry key returned by `store_search` contains multiple certificates. 
