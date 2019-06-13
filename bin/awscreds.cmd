@ECHO OFF

SET arg_count=0
FOR %%x in (%*) DO SET /a arg_count += 1

IF %arg_count% == 1 GOTO HAVEARGS
ECHO Usage: awscreds {profile}
EXIT /B 1

:HAVEARGS
SET PROFILE=%1
SET TEMPFILE=%TEMP%\awscreds.cmd
CALL getawscreds -p %PROFILE% -o %TEMPFILE%

IF EXIST %TEMPFILE% GOTO HAVEFILE
ECHO getawscreds did not produce an output file
EXIT /B 1

:HAVEFILE
ECHO Invoking %TEMPFILE%
%TEMPFILE%
