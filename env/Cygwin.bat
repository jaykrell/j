@if "%_echo%" == "" @echo off

call \dev2\j\env\clearenv

set PATH=%SystemDrive%\cygwin\bin;%PATH%
set CYGWIN=server

@rem reset errorlevel
dir > nul

Title gcc
