# Scenario 6

Cloud based Supply Chain Exploitation

## Prerequisites

- Pre-install Applications

```
# browser
sudo apt-get install firefox
# docker
sudo apt install apt-transport-https ca-certificates curl software-properties-common
## add official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
## update again
sudo apt update
sudo apt install docker-ce
## start docker service and enable it to run at boot
sudo systemctl start docker
sudo systemctl enable docker

# az command (mac)
brew update && brew install azure-cli

# az command (linux - Ubuntu)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

```

- Disable Firewall

    ```
    sudo ufw disable
    ```

- Disable Anti-Virus on Target Machine

    ```
    turn off real-time protection on Windows Machine
    
    ```


- Tailored Configuration on Azure   

    **to log important track on the cloud-based exploitation chain**

- Configuration on Port
    
    listening port of attack server (host 2) is on 8081 (avoid conflict with vweb on 8000), need to open inbound port on attacker machine to receive packed information
    

## Structure

- Stage1: vul_web:

    vweb.py: public web svc with accidental/debug leak

- Stage2: scripts:

    publish_to_repo: simulate publish to local repo/ + audit (uses leak.json text)

- Stage3: scripts:

    (1) malicious_build.py: simulate build-time injection (benign marker), the output will be packaged in package_artifact.sh

    (2) package_artifact.sh: package to dist/artifact.zip + sha256 + package log

    (3) publish_to_repo.sh: publish setup.py to Azure Blob

- Stage4: scripts:

    downstream_consume.sh: consume artifact → run benign payload → collect report


## Attack Steps

- 1. Leak a secret

    public repo with fake token using github and dummy repo

- 2. CI/CD system using secret

    github actions pipeline referencing it using github actions

- 3. Inject "Malicious" code

    alter a package during build using shell, python

- 4. download downstream progapation

    install altered package in another project

## Exploitation

- upload malicious package and rename it to artifact
```
az storage blob upload \
  --container-name artifacts \
  --file malicious_package.zip \
  --name artifact.zip \
  --account-name examplestorage
```


- How to trigger:

Three-stage exploitation works in sequential fashion

```
# first stage exploitation

```

- Evasion Method

    - obfuscated malicious scripts
    - multi-stage exploitations
    - remove generated local payloads
    - conditional trigger (random time)

- Attack Time (British Winter Time)

    - normal behavious: 2025.10.31 14:22
    - attack simulation starts: 2025.10.31 14:24

        - install packages: 14:26
        - start vulnerable web service: 14:26
        - simulated normal behaviour starts: 14:39

        - start to collect sensitive information: 14:47 
        - start to build malicious script for setup.py: 14:51

        - package the build artifact: 14:56

        - login in azure: 14:56

        - configure the credential information: 14:59

        - push to repo: 15:01

        - download task for downstreaming task (payload executed): 15: 03

        - exploitation failed: 15:05

        - rebuild malicious_script: 15:05

        - package the build artifact: 15:06

        - publish to repo: 15:06

        - downsteam task (payload triggered at random time): 15:09

        - shell callback to C2 sever: 15:15

        - Attacker Side Behaviour:

            - browser the disk space: 15:17
            
            - check running process: 15:18 

            - upload script with SenScanner.py: 15:21

            - load necessary running environment into target's memory (named packs): 15:24

            - start listening process: 15:28

            - (failed with module error) load script senscanner for sensitive information scanning and exfiltrate: 15:30

            - load new necessary running environment into target's memory (named packs): 15:33

            - (failed with module error) load script senscanner for sensitive information scanning and exfiltrate: 15:34

            - load new necessary running environment into target's memory (named packs): 15:37

            - (failed with module error) load script senscanner for sensitive information scanning and exfiltrate: 15:38

            - upload new script with SenScanner.py: 15:47

            - (failed with module error) load script senscanner for sensitive information scanning and exfiltrate: 15:47

            - upload new script with SenScanner.py: 15:54

            - upload new script with SenScanner.py to C:\Windows\unpacked: 16:04

            - upload new script with SenScanner.py to C:\Windows\unpacked: 16:13

            - receive packed results from SenScanner:  

            - load script to collection information: 16:14

            - upload script with SysScanner.py to C:\Windows\unpacked: 16:40

            - receive packed results from SysScanner: 

            - load script SenScanner to collection information: 18:16

            - new callback 21:42

            - Second Day (2025.11.1):

                - load_script SysScanner: 9:07

                - rebuild the callback: 10:34
        
                - load)script for SysScanner: 10:35
                
                - load module with new packages for library support: 10:38

                - load script: 10: 40

        - Target Side (2025.11.1):

            - rebuild everything from (python3 malicious_script.py): 10:45

        - Attack Side (2025.11.1):

            - got new callback: 10:51

            - load_modules: 10:51

            - got new callback: 11:17

        - Target Side:

            - new build process: 15:36

        - Attack Side:

            - new callback: 15:51
        
            - load test code: 15:52 

            - load script sysscanner: 15:53 failed

            - new callback: 16:21


- Data Collection and Analysis (under queries - virtual machine):

    - Collected Data Type:



## Simulation Steps:

**build up git and run all commands during git environment (powershell in specific steps, default with git bash)**

Host 1 - Target / Victim System, Host 2 - Attacker

```

## ------------ Configuration ----------------
# download python3 environment -- inside powershell with admin for windows
git clone https://github.com/pyenv-win/pyenv-win.git $env:USERPROFILE\.pyenv
setx PYENV "$env:USERPROFILE\.pyenv\pyenv-win"
setx PATH "$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims;$env:PATH"

# specify python version --- inside git bash
pyenv install 3.10
pyenv global 3.10
pyenv local 3.10

# create local environment
pyenv -m venv .venv
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
./.venv/Scripts/activate

# upgrade building tools - avoid compatibility problem
python -m pip install -U pip setuptools wheel build

# download zip --- inside PowerShell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install zip unzip

# download az with PowerShell
winget install -e --id Microsoft.AzureCLI

# host 2
allow inbound port 8081, 8000
# host 1
allow inbound port 8000

## ------------ Simulation Starts ----------------

# download necessary libraries (both hosts)
cd sc6
pip3 install -r requirements.txt

# scanning open port with services (host 2)
nmap -sV 51.143.216.192

# return results with:

PORT     STATE  SERVICE       VERSION
22/tcp   closed ssh
80/tcp   closed http
443/tcp  closed https
3389/tcp open   ms-wbt-server Microsoft Terminal Services
8000/tcp open   http-alt      Werkzeug/3.1.3 Python/3.10.11

# start server (host 1)
cd scripts
bash start_vweb.sh

# collect leak scerets (host 2)
bash collect_leak_from_vweb.sh

# malicious build (host 2)
python3 malicious_build.py

# package the build artifact (host 2)
bash package_artifact.sh

# need export some credential information here (host 2)
export AZURE_STORAGE_ACCOUNT=xxxx
export AZURE_CONTAINER=xxx

# need authentication (host 2)
export AZURE_STORAGE_KEY=xxx

# push to repo (host 2)
bash publish_to_repo.sh

# download task (host 1)
bash downstream_consume.sh

```

- automatic testing for all stages
```
sudo ./run_all.sh
```


## Problems

- unsupported modules (out of build-in libraries from medusa agent)

    ```
    # under existing environment -- find medusa Dockerfile
    cd Mythic/InstalledServices/Medusa/



    ```