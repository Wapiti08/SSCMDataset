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

- Open all the services for monitoring

    check the linux and docker based log monitoring at main readme.md

- To make sure consistent monitoring

```
# run all the log transformation scripts to consistently transfrom original logs
sudo python3 auditpip/audit.py
sudo python3 suricatapip/suricata_events_trans.py
sudo python3 suricatapip/suricata_logs_trans.py
sudo python3 traceepip/tracee.py
sudo python3 zeekpip/conn/zeek_conn.py
sudo python3 zeekpip/dns/zeek_dns.py
sudo python3 zeekpip/files/zeek_files.py
sudo python3 zeekpip/http/zeek_http.py

# (optional) simple shell to run all the above commands
chmod +x start_pipelines.sh
sudo ./start_pipelines.sh

# create crob jobs to transfer ndjson into json array every five seconds
crontab -e

*/5 * * * * sudo python3 ndjson_to_array.py /var/log/audit/audit.ndjson /var/log/audit/audit.json 2>&1 | sudo tee -a /var/log/audit/ndjson_audit.log > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /var/log/suricata/events.ndjson /var/log/suricata/events.json 2>&1 | sudo tee -a /var/log/suricata/ndjson_events.log  > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /var/log/suricata/suricata.ndjson /var/log/suricata/suricata.json 2>&1 | sudo tee -a /var/log/suricata/ndjson_suricata.log > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /tmp/tracee.ndjson /tmp/tracee.json 2>&1 | sudo tee -a /tmp/ndjson_tracee.log > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /opt/zeek/spool/zeek/conn.ndjson /opt/zeek/spool/zeek/conn.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_conn.log > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /opt/zeek/spool/zeek/dns.ndjson /opt/zeek/spool/zeek/dns.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_dns.log > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /opt/zeek/spool/zeek/http.ndjson /opt/zeek/spool/zeek/http.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_http.log  > /dev/null
*/5 * * * * sudo python3 ndjson_to_array.py /opt/zeek/spool/zeek/files.ndjson /opt/zeek/spool/zeek/files.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_files.log  > /dev/null

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





