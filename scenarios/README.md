## Scenarios Explanation

## Azure Instructions

- Prerequisites (for Mac):

    - download Windows APP (app store)
    - download RDP file from Azure
    - drag that file to Windows APP

- Prerequisties (for Ubuntu):
    ```
    # download Mythic
    - git clone https://github.com/its-a-feature/Mythic --depth 1
    # download docker
    sudo ./install_docker_ubuntu.sh
    sudo make
    # generate configuration file
    sudo ./mythic-cli start 
    
    # options for payloads or C2 profiles
    ## download c2 profile
    sudo ./mythic-cli install github https://github.com/MythicC2Profiles/http

    ## download agents --- for macOS only
    sudo ./mythic-cli install github https://github.com/MythicAgents/apfell
    ## download agents --- for linux and macOS
    sudo ./mythic-cli install github https://github.com/MythicAgents/poseidon
    ## download agents ---- for windows
     sudo ./mythic-cli install github https://github.com/MythicAgents/Apollo
    # download logging
    sudo ./mythic-cli install github https://github.com/MythicC2Profiles/basic_logger

    ## restart the service to integrate updates
    sudo ./mythic-cli restart

    # ========= for rdp configuration on Linux =======
    sudo apt install xfce4 xfce4-goodies -y
    sudo apt install xrdp -y
    echo xfce4-session > xsession
    sudo systemctl restart xrdp

    # add inbound rule on Networking settings with 3389
    # use Windows APP (download from apple store) with IP:3389 and the credentials

    # download browser for Web UI
    sudo apt-get install firefox
    # check the status of Mythic
    sudo ./mythic-cli status
    # access the webUI by loading https://127.0.0.1:7443
    # default username and password are stored in .env
    # check 'MYTHIC_ADMIN_USER' and 'MYTHIC_ADMIN_PASSWORD'
    ```

## C2 Server Configuration

- How to create payload:

    - follow the instructions to create a payload for http
    
    - configure the parameters and copy them as agent_config inside setup.py

    - download the generated payload --- apfell.js

    - remote copy to local file
    ```
    scp username@remote_host:/path/to/remote/apfell.js /path/to/local/destination

    ```

- Run payload (MAC)

    ```
    osascript -l apfell.js
    ```

## APT Functions Explanation