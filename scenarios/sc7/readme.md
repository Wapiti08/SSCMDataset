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

- To make sure consistent monitoring

```
# run all the log transformation scripts to consistently transfrom original logs
# go to corresponding folders
python3 audit.py
python3 suricata_events_trans.py
python3 suricata_logs_trans.py
python3 tracee.py
python3 zeek_conn.py
python3 zeek_dns.py
python3 zeek_files.py
python3 zeek_http.py

# create crob jobs to transfer ndjson into json array every five seconds

*/5 * * * * python3 ndjson_to_array.py --input /var/log/audit/audit.ndjson --output /var/log/audit/audit.json >> /var/log/audit/ndjson_audit.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /var/log/suricata/events.ndjson --output /var/log/suricata/events.json >> /var/log/suricata/events/ndjson_events.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /var/log/suricata/suricata.ndjson --output /var/log/suricata/suricata.json >> /var/log/suricata/ndjson_suricata.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /tmp/tracee.ndjson --output /tmp/tracee.json >> /tmp/ndjson_tracee.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /opt/zeek/spool/zeek/conn.ndjson --output /opt/zeek/spool/zeek/conn.json >> /opt/zeek/spool/zeek/ndjson_conn.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /opt/zeek/spool/zeek/dns.ndjson --output /opt/zeek/spool/zeek/dns.json >> /opt/zeek/spool/zeek/ndjson_dns.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /opt/zeek/spool/zeek/http.ndjson --output /opt/zeek/spool/zeek/http.json >> /opt/zeek/spool/zeek/ndjson_http.log 2>&1
*/5 * * * * python3 ndjson_to_array.py --input /opt/zeek/spool/zeek/files.ndjson --output /opt/zeek/spool/zeek/files.json >> /opt/zeek/spool/zeek/ndjson_files.log 2>&1

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

## Method

- Exploit Malicious Model and Lamdba function

    insert malicious code inside trained model

## Exploitation

- How to trigger:

    - loading model to do prediction or other work
    ```
    # build docker instance -- under service folder
    sudo docker build -t m-model .

    # Run the Docker container
    sudo docker run -p 5001:5001 -v $(pwd)/output:/app/output m-model

    # the above command will open a server on port 5001
    # go to Web page with 127.0.0.1:5001

    # provide the interface with different images with numbers inside

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





