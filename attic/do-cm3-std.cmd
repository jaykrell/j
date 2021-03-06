@REM #!cmd.exe
@REM $Id$

@if "%_echo%" == "" @echo off

call %~dp0clearenv.cmd
setlocal
call %~dp0sysinfo.cmd || goto :eof
call %~dp0pkginfo.cmd
call %~dp0pkgcmds.cmd

call %~dp0def-std-pkgs.cmd

REM
REM UNDONE
REM
REM type m3bundle >/dev/null 2>/dev/null || \
REM   . "$ROOT/scripts/do-pkg.sh" buildship m3bundle

call %~dp0pkgcmds extract_options %*
call %~dp0pkgcmds map_action %* || goto :eof
call %~dp0pkgcmds add_action_opts %*

call :echo_and_run call %~dp0pkgmap.cmd %OPTIONS% %ADDARGS% -c "%ACTION%" %P%

endlocal
goto :eof

:echo_and_run
setlocal
set x=%*
set x=%x:  = %
set x=%x:  = %
echo %x%
%x%
endlocal
goto :eof
