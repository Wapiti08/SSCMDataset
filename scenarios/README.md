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
    ## option 1
    sudo ./mythic-cli install github https://github.com/MythicC2Profiles/http

    # download logging
    sudo ./mythic-cli install github https://github.com/MythicC2Profiles/basic_logger

    # ========= for rdp configuration on Linux =======
    sudo apt install xfce4 xfce4-goodies -y
    sudo apt install xrdp -y
    echo xfce4-session > xsession
    sudo systemctl restart xrdp

    # add inbound rule on Networking settings with 3389
    # use Windows APP (download from apple store) with IP:3389 and the credentials

    ```
- attack machine:

    connect via bastion


## APT Functions Explanation