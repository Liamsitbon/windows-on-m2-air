@echo off
setlocal
rem Explicit offline store only; never silently edits the current Windows store.
if "%~1"=="" goto usage
if not exist "%~1" (
  echo BCD store does not exist.
  exit /b 2
)
bcdedit /store "%~1" /enum all
if errorlevel 1 exit /b 1
if /I not "%~3"=="apply" exit /b 0
if "%~2"=="" goto usage
bcdedit /store "%~1" /enum "%~2"
if errorlevel 1 exit /b 1
if exist "%~1.before-boot-details" (
  echo Backup already exists; inspect it before changing the store.
  exit /b 2
)
copy /b "%~1" "%~1.before-boot-details" >nul
if errorlevel 1 exit /b 1
bcdedit /store "%~1" /set "%~2" sos on
if errorlevel 1 goto failed
bcdedit /store "%~1" /set "%~2" bootlog yes
if errorlevel 1 goto failed
bcdedit /store "%~1" /enum "%~2"
exit /b %errorlevel%
:failed
echo A setting failed. Original store is preserved in .before-boot-details.
exit /b 1
:usage
echo Usage: windows-boot-details.cmd "path-to-BCD" ["loader-identifier" apply]
echo Without apply this only enumerates the named offline store.
exit /b 2
