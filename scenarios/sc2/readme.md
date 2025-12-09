## Attack Detail

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


    - Create / Decompile RunTime.exe
        ```
        # decode
        python pyinstxtractor.py test.exe
        # encrypt (need pyinstaller)
        pyinstaller --onefile yourscript.py
        # encrypt and output one file
        pyinstaller --onefile --windowed yourscript.py
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



