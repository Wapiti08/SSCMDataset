# LayerInj(SC7)

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

- Virtual Environment (Pyenv) for Python
```

sudo apt update
sudo apt install --no-install-recommends make build-essential \
  libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
  curl git ca-certificates libncursesw5-dev xz-utils tk-dev \
  libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
curl https://pyenv.run | bash

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc

source ~/.bashrc

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

    **the data to ingest inside Azure log workspace has to be ndjson format, the example to parse format is different, which is json array format. **


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


<!-- # need to put script to path first before creating crontab jobs
sudo cp ndjson_to_array.py /usr/local/bin/
sudo chmod +x /usr/local/bin/ndjson_to_array.py

# create crob jobs to transfer ndjson into json array every five seconds
sudo crontab -e

# then add the following jobs inside crontab
*/5 * * * * /usr/local/bin/ndjson_to_array.py /var/log/audit/audit.ndjson /var/log/audit/audit.json 2>&1 | sudo tee -a /var/log/audit/ndjson_audit.log > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /var/log/suricata/events.ndjson /var/log/suricata/events.json 2>&1 | sudo tee -a /var/log/suricata/ndjson_events.log  > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /var/log/suricata/suricata.ndjson /var/log/suricata/suricata.json 2>&1 | sudo tee -a /var/log/suricata/ndjson_suricata.log > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /tmp/tracee.ndjson /tmp/tracee.json 2>&1 | sudo tee -a /tmp/ndjson_tracee.log > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /opt/zeek/spool/zeek/conn.ndjson /opt/zeek/spool/zeek/conn.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_conn.log > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /opt/zeek/spool/zeek/dns.ndjson /opt/zeek/spool/zeek/dns.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_dns.log > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /opt/zeek/spool/zeek/http.ndjson /opt/zeek/spool/zeek/http.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_http.log  > /dev/null
*/5 * * * * /usr/local/bin/ndjson_to_array.py /opt/zeek/spool/zeek/files.ndjson /opt/zeek/spool/zeek/files.json 2>&1 | sudo tee -a /opt/zeek/spool/zeek/ndjson_files.log  > /dev/null -->

```

- Add Data Sources

    follow the path to add corresponding log source to pre-defined custom tables:

    Data Collection Rule -> Configuration -> Data sources -> Add -> Define log source; tables; destination

## Make Payload

```
# convert malicious payload into shorter link
python3 shorter_link.py

# replace the link inside model.py for request

# to generate trained model --- under service folder
python3 train.py
```

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

- Attack Timeline ((Dev_Linux: host1, Attack: host2)):

    - host1:

        - generate model 2025.12.8 (10:43)
        ```
        python3 train.py
        ```

        - build docker instance (10.59)
        ```
        sudo docker build -t m-model .
        ```

        - open the service api (11:03)
        ```   
        sudo docker run -p 5001:5001 -v $(pwd)/output:/app/output m-model

        ```
        after it successfully runs, open web UI and access 127.0.0.1:5001

        - try with different image (11:06)

        got module import error

        - rebuild docker instance (11:15)

        - restart servicd api

        payload download is triggered when the prediction is '3' (11:16)

    - host2:

        - open server for listenning (10:50)

        - check folder system and process (11:17)

        - load_script for information gathering (11:19)

            got response for data exfiltration (11:20)


- Ground Truth:

    - core IOCs with locations and numbers:
        - eve.json - Attack IP 20.93.23.234 (238 lines)

        ▸ zeek_conn.csv — Attack IP 20.93.23.234 (155 lines):

            - Port 80 (C2 HTTP): 153 lines
              (2591,2623,2650,2662,2672,2684,2695,2701,2716,2727,
              2745,2755,2765,2777,2790,2805,2816,2822,2834,2839,
              2860,2873,2884,2894,2904,2916,2928,2947,2956,2967,
              2980,2994,3012,3024,3039,3049,3059,3071,3083,3092,
              3104-3105,3111-3112,3124-3125,3139-3140,3156,3165,
              3173,3178,3186,3196,3206,3211,3221,3230,3246,3264,
              3274,3286,3300,3314,3324,3330,3340,3350,3360,3379,
              3395,3405,3414,3421,3432,3441,3452,3462,3476,3486,
              3495,3505,3522,3531,3541,3552,3561,3569,3575,3585,
              3595,3606,3621,3635,3640,3650,3662,3673,3682,3694,
              3700,3706,3716,3728,3741,3753,3762,3772,3784,3793,
              3805,3810,3824,3832,3846,3863,3878,3888,3898,3911,
              3921,3927,3939,3945,3957,3970,3987,4006,4017,4022,
              4034,4040,4053,4064,4074,4088,4099,4113,4133,4141,
              4146,4156,4166,4175,4184,4196,4206,4213,4225,4235,
              4249,4259,4269)

            - Port 8081 (data exfiltration): 2 lines
              Line 3106: 10.0.0.4:43716 → 20.93.23.234:8081 (11:20:06)
              Line 3113: 20.93.23.234:8081 → 10.0.0.4:43716
                         (226 bytes sent to victim, exfil delivery)

        ▸ zeek_http.csv — C2 HTTP callbacks (77 lines):

            - Lines: 314,318,322,326,328,336,340,344,347,350,357,360,
              364,368,370,374,381,385,387,391,395-396,398-399,406,
              410,412,416,419,427,430,437,439,443,447,456,458,462,
              466,470,472,479,483,486,489,493,500,502,506,509,512,
              516,523,525,529,532,535,540,547,550,554,556,561,568,
              572,575,578,582,586,593,595,599,602,606,609,616,620
            - Time range: 11:16:33 → 11:29:37 (~13 min, every ~10s)
            - Response sizes:
                432 bytes: 1 req (line 314 — initial callback/check-in)
                176 bytes: 73 reqs (heartbeat/keepalive)
                392 bytes: 1 req (line 395 — command response)
                264 bytes: 1 req (line 399 — command response)
                15068 bytes: 1 req (line 396 — large payload, likely
                  load_script for info gathering at ~11:19)

        ▸ zeek_files.csv — C2 file transfers (77 lines):

            - Lines: 306,310,314,318,320,327,331,335,338,341,348,351,
              355,359,361,365,372,376,378,382,386-387,389-390,397,
              401,403,407,410,417,420,427,429,433,437,444,446,450,
              454,458,460,467,471,474,477,481,488,490,494,497,500,
              504,511,513,517,520,523,527,534,537,541,543,548,555,
              558,561,564,568,572,579,581,585,588,592,595,602,606
            - 1:1 correspondence with zeek_http entries (HTTP file
              objects from C2 callbacks)


     - attack timeline (all times UTC):
        - 10:43: python3 train.py (model generation — not in logs,
          pre-logging)
        - 10:59:33: docker build -t m-model . (azure_syslog line 831)
        - 11:04:01: docker run -p 5001:5001 m-model (line 2084, first run)
        - 11:06: module import error (attempted prediction, no log trace)
        - 11:14:21: docker build -t m-model . (line 9613, rebuild)
            → docker registry DNS at 11:14:21 (zeek_dns lines 549-552)
        - 11:15:47: docker run -p 5001:5001 m-model (line 8278, restart)
        - 11:16:33: first C2 callback to 20.93.23.234:80
            (zeek_http line 314, 432 bytes response —
            payload triggered when prediction='3')
        - 11:16:33→11:29:37: periodic C2 beaconing every ~10s
            (77 HTTP requests, 73 × 176-byte heartbeats)
        - ~11:19: load_script uploaded (15068-byte response, line 396)
        - 11:20:06: data exfiltration on port 8081
            (zeek_conn lines 3106,3113 — 226 bytes sent to victim)

    - total unique IOC records: 635 lines