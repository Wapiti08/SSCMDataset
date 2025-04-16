# SSCMDataset
monitoring dataset for software supply chain vulnerabilities

## Monitoring Setting Ups

- Monitoring Platform
    - LimaCharlie

- Covered Log Sources

    - Network Traffic

        - zeek
        - wireshark

    - Process Execution


    - System Logs


## Simulated Normal Behaviour

- office work (1)

- web visit (2)
 
- remote ssh (3)

- scp for file copy (4)

- open software and call update (5)

- download repository (6)

- automatic development (pip, compile) (7)

- openai (gpt service)(8)

- login behavior (9)

## Factors for Randomness

- idle time

- randomization

## Multi-Souce Data Monitoring and Data Collection

- Data Monitor:

    use Azure Log Analytics Workspace to monitor data with multi-source agents

    - covered sources:

        - Windows:

            - Windows event - Built-in data source

                - Application
                - Security
                - System

            - Process creation, network connections, registry changes, file modifications

                - configure Sysmon on Windows machine

                ```
                # download sysmon-config.xml from monitor folder
                Sysmon64.exe -accepteula -i sysmon-config.xml
                # output to custom path --- create Logs first under C disk
                wevtutil epl Microsoft-Windows-Sysmon/Operational C:\Logs\sysmon.evtx

                ```

            - Firewall logs
                
                configured after defining data collection endpoint

        - Linux:

            - Syslog -- built-in source

            - Process creation, network connections, registry changes, file modifications

                - configure Sysmon (Linux version) on Linux machine

            - Audit

                ```
                sudo pat install auditd -y
                # configure /etc/audit/audit.rules or rules.d/audit.rules
                # log saved to /var/logs/audit/audit.log
                ```

            - Network Traffic

                ```
                sudo apt install zeek
                sudo zeek -i eth0 {depends on system network inferfaces}
                # /usr/local/zeek/logs/current
                ```

            - Packet capture, protocol detection

                ```
                sudo apt install suricata
                # config file /etc/suricata/suricate.yaml
                # logs saved to /var/log/suricata

                ```

        - Mac:

            - System logs, security events, app behaviour
            ```
            # check logs under /var/db/diagnostics
            # check system logs under /var/log/*
            ```

            - Network traffic:
            ```
            # rotate by time: 1 file per 5 minutes
            sudo tcpdump -i eth0 -G 300 -w "/var/log/tcpdump/log_%Y-%m-%d_%H-%M-%S.pcap"

            ```

    - Agent configuration:

        1. Create a Log Analytics workspace (make sure the owner and admin privilege for this resource)

        2. Select monitor VMs

        3. Add resources (where attack and victim machines locate)

        4. Click "Enable Data Collection Endpoints"

        5. "Add data source" -> select Windows Event Logs and Syslog, [Firewall logs]
        
            - Firewall logs configuration:

                - [Define Data Collection Rules (DCR)](https://learn.microsoft.com/en-us/azure/azure-monitor/vm/data-collection)

                - Configure data collection endpoints to cover firewall logs 

                - Choose all categories: domain, private, public

    - Add Destination:





- data collection:




## Details of Host Configuration

- wins dev

    - IP:

    - Pre-installed Software
        - vs code, filezilla, pip, python, git, MobaXterm, discord, 1password
    
    - Open Services
        - ssh
    
    - Simulated Behaviours

    - Sensititive Information
        - credentials (.txt, .ini)
        - configuration files (.conf, .ini, .xml)
        - system information


- linux dev

    - IP:

    - Pre-installed Software
        - vs code, docker, python, pip, git, slack, discord, 1password
    
    - Open Services
        - ssh
    
    - Simulated Behaviours

    - Sensititive Information
        - credentials (.txt, .ini)
        - configuration files (.conf, .ini, .xml)
        - system information


- wins office

    - IP:

    - Pre-installed Software
        - firefox, zoom, skype, slack, discord, 1password
        - office set
    
    - Open Services
    
    - Simulated Behaviours

    - Sensititive Information
        - financial spreadsheets (.xls, .xlsx, .csv)
        - documents (.docx, .pdf)
        - intellectual property (IP) (.pptx, .py, .js)
        - configuration files (.conf, .ini, .xml)
        - broswer history / cache
        - system information


- wins server
    - IP:

    - Service：
        - ssh
        - web service (less-strict acl)
        - dns service (less-strict acl)
        - database (strict acl): SQL Server
        - open logging service

    - Sensititive Information
        - database data
        - logs
        - system information

## Collected Logs

- process execution
- system logs (audit, application, security)
- network traffic (zeek)
- services (web, ssh, database, access)


## Simulation Steps

- See detail in individual scenarios


## Running Instructions
```
pyenv global 3.10.1
pyenv local 3.10.1
# make sure pyenv has been configured before
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```