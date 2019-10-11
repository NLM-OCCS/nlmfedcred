# Cracking the Smart Card puzzle

## Resources

- MSDN Blog [How to read a certificate from a smart card and...](https://blogs.msdn.microsoft.com/winsdk/2010/05/28/how-to-read-a-certificate-from-a-smart-card-and-add-it-to-the-system-store/)
- Chromium appears to be written in Python, and to use ctypes as well - [source code](https://chromium.googlesource.com/chromium/tools/depot_tools.git/+/master/fix_encoding.py)

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