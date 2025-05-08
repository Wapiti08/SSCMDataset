# Scenario 8

Trojaned Neural Networks

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


## Exploitation

- Exploit Malicious Model and Lamdba function

    insert malicious code inside trained model

- How to trigger:

    when loading model to do prediction or other work
    ```
    # build docker instance
    docker build -t m-model .

    # Run the Docker container
    docker run m-model
    ```

## Steps for Payload Creation



