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

# az command
brew update && brew install azure-cli

```

- Disable Firewall

```
sudo ufw disable
```

- Disable Anti-Virus on Target Machine

    turn off real-time protection on Windows Machine


- Tailored Configuration on Azure

**to log important track on the cloud-based exploitation chain**

```

```

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

## Simulation Steps:

**build up git and run all commands during git environment (powershell in specific steps)**

```
# download python3 environment -- into powershell for windows
git clone https://github.com/pyenv-win/pyenv-win.git $env:USERPROFILE\.pyenv
setx PYENV "$env:USERPROFILE\.pyenv\pyenv-win"
setx PATH "$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims;$env:PATH"

# specify python version
pyenv install 3.10
pyenv global 3.10

# create local environment
pyenv virtualenv 3.10 SSCMDataset
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv activate SSCMDataset

# upgrade building tools - avoid compatibility problem
python -m pip install -U pip setuptools wheel build

# download zip with PowerShell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install zip unzip

# download az with PowerShell
winget install -e --id Microsoft.AzureCLI

# download necessary libraries
cd sc6
pip3 install -r requirements.txt

# start server
cd scripts
bash start_vweb.sh

# collect leak scerets
bash collect_leak_from_vweb.sh

# malicious build
python3 malicious_build.py

# package the build artifact
bash package_artifact.sh

# login in azure first
az login

# push to repo
bash publish_to_repo.sh

# download task
bash downstream_consume.sh

```

- automatic testing for all stages
```
sudo ./run_all.sh
```

## Steps for Payload Creation


```
pip install -r requirements.txt

export HOST=0.0.0.0 PORT=5000
export LEAK_MODE=mask           # or "auto" to simulate accidental leaks
export APP_ENV=prod             # "dev"/"staging" will look internal (auto mode)
export TRUST_PROXY_HEADERS=false

# run test
sudo chmod +x tests/run_debug_tests.sh

# enter into step1 folder
python vweb.py


```
