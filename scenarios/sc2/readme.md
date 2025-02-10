## Attack Detail

- Prepare：

    - download [pyenv-win](https://pyenv-win.github.io/pyenv-win/docs/installation.html#pyenv-win-zip)
    
    - configure python version with 3.10:
        ```
            pyenv install 3.10
            pyenv global 3.10
        ```

- Attack Steps

    - simulated normal behaviour for daily operation (increase noise) 

        - Windows Dev Host (download python package):
            
            - Pre-installed Software
                - vs code, filezilla, pip, python, git, MobaXterm, discord, 1password
            
            - Simulated Behaviours
                - 2, 3, 4, 5, 6, 7

    - payload execution

        ```
            python3 setup.py # under pystallerer-1.0.0

        ```
        The involving actions:
        - Downloads a potential malware (Runtime.exe) from an external server.

        - Uses Windows Startup Folder to achieve persistence, ensuring the malware runs after every reboot.
        
        - Executes silently using VBS scripts and batch files.
        
        - Avoids detection by placing files in Windows system directories.

- Trigger

    under executing setup.py --- automatically trigger the download and execution of payload

- Evasion Method

    - sophisticated encryption method
    - file replacement
    - earse trace

- Data Exfiltration

    - extract system info to C2 server

