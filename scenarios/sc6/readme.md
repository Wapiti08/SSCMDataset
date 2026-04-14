# CloudEX(SC6)

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
bash downstream_consume.sh

# this code will automatically trigger the download payload and execute following two-stage exploitation
```

- Evasion Method

    - obfuscated malicious scripts
    - multi-stage exploitations
    - remove generated local payloads
    - conditional trigger (random time)

- Attack Time (British Winter Time)

    Host 1 - Target / Victim System, Host 2 - Attacker
    
    - normal behavious simulation starts : 2025.11.13 (11:11) 
    - attack simulation starts (host1): 

        - start vulnerable web service (host1): 11:13

        - start to collect sensitive information (host2): 11:23

            found exposed sensitive credential 

        - start to build malicious script for setup.py (host2): 11:24 

            export credentials

        - package the build artifact (host2): 11:25 

        - push to repo (host2): 11:26

            leave reasonable time for victim to trigger malicious setup.zip

        - (also need to export credentials) download task for downstreaming task (payload executed) (host1): 11:42

        - return callback (host2): 11:44

        - check running process of target system (host2): 11:45

        - check files of target system (host2): 11:45

        - try to download C://Windows (host2): 11:47 - failed 

        - try to download C:\package (host2): 11:48 - failed

        - open listening port for data exfiltration (host2): 11:49

        - upload custom script 1 (run in memory) to collect sysinfo (host2): 11:49

        - return result (compressed zip file) from script 1: 11:50

        - upload custom script 2 (run in memory) to collect sensitive files (host2): 11:52

        - further reconnaissance (nmap): 12:12

            ignore 3389 (open for simulation), no other interesting ports are open (no specific service)

        - return result (compressed zip file) from script 2: 12:22



- Data Collection and Analysis (under queries - virtual machine):

    - Collected Data Type:

        - Attack Side Logs

        - Victim Side Logs

        - Custom Logs

            - \scenarios\\logs\\state.log

    
    - MITRE ATT&CK Collection (host2 - Mythic C2 UI)


## Simulation Steps:

**build up git and run all commands during git environment (powershell in specific steps, default with git bash)**

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

# create local environment (direct virtualenv)
python3 -m venv .venv
./.venv/Scripts/activate

# if without pyenv
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

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

# scanning open port with services (host 2)
nmap -sV 51.143.216.192

# return results with:

PORT     STATE  SERVICE       VERSION
22/tcp   closed ssh
80/tcp   closed http
443/tcp  closed https
3389/tcp open   ms-wbt-server Microsoft Terminal Services
8000/tcp open   http-alt      Werkzeug/3.1.3 Python/3.10.11

```

- Ground Truth:

    - core IOCs with locations and numbers:

        - malicious payload delivery (downstream_consume.sh):
            - downstream_consume.sh execution: 29 lines
              (2818-2820,3268-3275,3277,3284-3285,3295-3302,
              3323-3324,3347-3351)
              First run at 11:41:07, second run at 11:42:30

        - malicious setup.py execution:
            - setup.py from artifact/downstream/unpacked/: 19 lines
              (3349,3351-3364,3366,3368-3370)
              At 11:42:37, "python3 setup.py --name" triggered by
              downstream_consume.sh
            - artifact/downstream/unpacked references: 39 lines
              (3272,3285-3291,3294,3296,3298,3300,3349-3370,
              3378-3379,3416-3417,3422)

        - attack IP: 20.93.23.234
            - total: 307 lines
            - credential collection via port 8000 (11:23):
              lines 1717-1724 (inbound from 20.93.23.234 to 8000)
            - nmap recon (12:12): lines 51-56,61,63,65-66
              (inbound scans from 20.93.23.234 to 8000)
            - C2 callback/exfil connections throughout

        - suspicious ports:
            - 8000 (vulnerable web service, Werkzeug): 56 inbound records
            - 8081 (data exfiltration): 2 outbound records
              lines 4415,6515
              (10.0.0.5 → 20.93.23.234:8081 at 11:49 and 12:22)

        - data exfiltration:
            - script 1 results (sysinfo zip): ~11:50
              line 4415: python3 → 20.93.23.234:8081
            - script 2 results (sensitive files zip): ~12:22
              line 6515: python3 → 20.93.23.234:8081

        - total attack-specific IOC records: ~392 

        - total unique IOC records: 377