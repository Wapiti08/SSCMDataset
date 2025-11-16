# Scenario 7

Trojaned Neural Networks

## Prerequisites

- Pre-install Applications

```
# git
sudo apt-get update
sudo apt-get install git

# browser
sudo apt-get install firefox
# docker
sudo apt install apt-transport-https ca-certificates curl software-properties-common
## add official GPG keycd ser   
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

- Remove experiment cache
```
# avoid no left disk space 
docker system prune -a
```

## How to make stealthy payload

```
# convert malicious payload into shorter link
python3 shorter_link.py

# replace the link inside model.py for request

# to generate trained model --- under service folder
python3 train.py
```

## Problems

- there is no exception from exec(m_code), but there is no callback shell

## Exploitation

- Exploit Malicious Model and Lamdba function

    insert malicious code inside trained model

- How to trigger:

    - loading model to do prediction or other work
    ```
    # build docker instance -- under service folder
    sudo docker build -t m-model .

    # Run the Docker container
    sudo docker run -p 5001:5001 -v $(pwd)/output:/app/output m-model

    # trigger when meeting specific input -- like image '3'

    ```

    - other helper actions
    ```
    # to show running instance
    sudo docker ps -a
    # to delete an image
    ## stop the image first
    sudo docker stop image_id
    ## remove image
    sudo docker rmi image_id -f
    ## delete all images
    sudo docker rm -vf $(sudo docker ps -aq)
    sudo docker rmi -f $(sudo docker images -aq)

    # enter inside an image
    sudo docker exec -it {container_id} /bin/bash
    # enter inside when building
    docker run -it --entrypoint /bin/bash model_name
    # Once inside:
    cat /app/model.py

    # rebuild without cache
    sudo docker build --no-cache -t m-model .
    ```

## Steps for Payload Creation



