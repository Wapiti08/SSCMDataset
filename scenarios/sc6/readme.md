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

```

- Disable Firewall

```
sudo ufw disable
```


- Tailored Configuration on Azure

**to log important track on the cloud-based exploitation chain**

```

```


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


## Steps for Payload Creation


```
pip install -r requirements.txt

export HOST=0.0.0.0 PORT=5000
export LEAK_MODE=mask           # or "auto" to simulate accidental leaks
export APP_ENV=prod             # "dev"/"staging" will look internal (auto mode)
export TRUST_PROXY_HEADERS=false
# enter into step1 folder
python vweb.py

```
