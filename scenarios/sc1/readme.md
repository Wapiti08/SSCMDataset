## Stegano (SC1)

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

- Attack Timeline (British Summer Time - UTC +1)

    ** Time in Target Windows System is one hour ahead **

    - normal behaviour: 2025.4.22 14:17 
    - attack behaviour: 2025.4.22 14:22

        - install package: 2025.4.22 14:22
        - (attack side) received callback: 2025.4.22 14.23
        - (attack side) browser the disk space
        - (attack side) upload script "SenScanner.py": upload to any writable folder (rejected for few times)
            - find writable folder at: C:\Windows\Temp\
        
        - (attack side) check from Mythic UI -- Files -- Uploads 
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


- Ground Truth:

     - core IOCs with locations and numbers:

        - package name: 
            - colorsapi-6.6.7 (with setup.py)
                - locations: sanidata/sc1/windows/azure_process.csv (52-88,133,148,196,295,406)
                - numbers (records/lines): 42
        
        - attack ip: 20.93.23.234
            - locations: 
                - azure_events (239-268,271,273-275,278-284,286,291,293-294,
                  297,300-302,319,345,377,405,408,413-415,420,433,450,493,
                  503,506,511,513-515,517-518,533-535,537-539,541-562,
                  564-611,613-616,619-620,622-662,665,667,670-675,677-691,
                  701-702,705-725,727-738,740,746-749,752-753,755,758,760,
                  762-786,788-809,811,813-814,816-837,839-887,889-893,896,
                  898-899,902-903,905-939,942,944-945,947-966,972-987,
                  989-990,993-994,996,999-1001)
                - azure_conn (597,629,696,769,863,884,953,1047,1065,1091,
                  1150,1167,1197,1232,1257,1322,1358,1390,1422,1487,1511,
                  1537,1569,1611,1642,1698,1724,1758,1778,1802,1825,1849,
                  1876,1967,1987,2011,2036,2064,2125,2151,2177,2244,2265,
                  2291,2315,2336,2403,2426,2461,2486,2508,2533,2550,2578,
                  2597,2620,2642,2662,2683,2706,2728,2750,2782,2810,2844,
                  2912,2940,2989,3052,3071,3097,3178,3204,3224,3283,3341,
                  3367,3413,3478,3498,3525,3587,3604,3621,3644,3665,3683,
                  3705,3728,3787,3802,3823,3842,3897,3923,3941,3961,3977,
                  3996,4020,4036,4052,4067,4086,4148,4170,4189,4211,4233,
                  4275,4292,4329,4374,4431,4447,4462,4478,4532,4572,4588,
                  4604,4622,4641,4658,4679,4699,4719,4777,4800,4815,4836,
                  4853,4874,4891,4911,4930,4945,5018,5482,5541,5603)
            - numbers: 614 total (473 in azure_events + 141 in azure_conn)

        - suspicious port: 80 (HTTP, unencrypted)
            - All 614 connections to 20.93.23.234 use destination port 80
            - NOTE: No port 8080 or 8000 found in ANY of the 5 files

        - data exfiltration: via python3/python → 20.93.23.234:80
            - locations: azure_conn (same 141 lines as attack ip above)
            - BytesSent (outbound/exfil): ~2.1 MB total
            - BytesReceived (inbound/download): ~265 MB total
              (individual downloads up to ~3.9 MB each — consistent 
              with image file downloads as described in the attack)
            - NOTE: The large inbound volume (~265 MB over 141 connection 
              windows) strongly suggests repeated image file downloads 
              from the C2 server. File creation events to C:\Windows\Temp 
              in azure_events only show PowerShell PSScriptPolicyTest 
              files (lines 288, 742) — the actual image write by 
              setup.py may fall outside Sysmon's file-create rule scope 
              or the captured time window.

    - total unique records: 656

    
- Troubleshooting:

    - No response from callback:

        need to run the installation process again to return a new callback
    
    - DLL load failed while importing xxx

        Installing the Visual C++ Redistributable for Visual Studio 2015 from this links: https://www.microsoft.com/en-us/download/details.aspx?id=48145 fixed the missing DLLs.
    

- Data Collection and Analysis:

    - Collected Data Type:

        - Event: This table includes all types of Windows Event Logs, like Application, System, and Setup logs.

        - SecurityEvent: Contains Windows Security Event Logs, often associated with auditing and security monitoring.

        - VMConnection: Tracks network connections to/from the VM
        
        - Perf: Contains performance metrics like CPU, memory, disk I/O, and network usage collected from VMs
        
        - BoundPort: Logs information about network ports that are bound (i.e., listening) on a VM
        
        - Process: Contains data about processes running on the VM

    - PreProcessing

        - select time scope under Monitoring - Logs - Query - Share

            2025.4.22 14:17 - 2025.4.22 16:20

    - Analysis

        - monitor -> label -> sc1 -> ioc_match.ipynb


    - Involve Techniques (more detailed information can be found at attack_navigator.json):
    
        - attack_navigator_cmds
        - attack_navigator_tasks

