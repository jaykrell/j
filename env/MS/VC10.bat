@if "%_echo%" == "" @echo off

call \dev2\j\env\clearenv

call \msdev\10\bin\msvcvars

@set DevEnvDir=
@set FrameworkDir=
@set FrameworkSDKDir=
@set FrameworkVersion=
@set MSVCDir=
@set LIBPATH=
@set VCINSTALLDIR=
@set VSINSTALLDIR=

@rem reset errorlevel
dir > nul

Title VC10
