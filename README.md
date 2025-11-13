# SSCMDataset
monitoring dataset for software supply chain vulnerabilities

![Python](https://img.shields.io/badge/Python-3.10-brightgreen.svg) 

## Covered Advanced Supply Chain Exploitations

- Stegano: Malicious code hides inside a typosquatting package and an infected image to stealthily exfiltrate system data.

- Starter: A typosquatting package abuses Windows startup and file replacement to persist and exfiltrate data via a Discord webhook.

- Parallel: A malicious NPM package chain executes parallel scripts to collect and compress system/sensitive data for exfiltration.

- NPMEX: Two coordinated NPM dependencies sequentially fetch and run remote payloads to steal sensitive information.

- 3CX: Trojanized installation software deploys multi-stage malware to steal browser data using obfuscation and DLL side-loading.

- CloudEX: Attackers exploit exposed CI/CD cloud credentials to modify artifacts and insert multi-stage data-stealing malware.

- LayerInj: A condition-triggered malicious function inside a Docker environment downloads fileless payloads to steal data.

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

            - Default Windows Events 

                - Application
                - Security
                - System
                - Custom Events:

                    - Microsoft-Windows-PowerShell/Operational!* : Obfuscated commands, encoded payloads, PowerShell-based malware
                    - Microsoft-Windows-WMI-Activity/Operational!* : Fileless malware, lateral movement, persistence via WMI
                    - Microsoft-Windows-Security-Audit-Configuration-Client/Operational!* : Brute force, privilege escalation, suspicious logins
                    - Microsoft-Windows-AppLocker/MSI and Script!* : Blocked or allowed execution of potentially malicious binaries/scripts
                    - Microsoft-Windows-AppLocker/EXE and DLL!* : Blocked or allowed execution of potentially malicious binaries/scripts
                    - Microsoft-Windows-TaskScheduler/Operational!* : Persistence mechanisms via scheduled tasks
                    - Microsoft-Windows-RemoteDesktopServices-RdpCoreTS/Operational!* : Lateral movement, brute force attempts
                    - Microsoft-Windows-Application-Experience/Program-Telemetry!* : Unusual or unknown binaries running
                    - Microsoft-Windows-DNS-Client/Operational!* : Beaconing, data exfiltration, C2 domains

                    To enable them on Windows System
                    ```
                        # give one example
                        wevtutil sl "Microsoft-Windows-Sysmon/Operational" /e:true
                    
                    ```

            - Process creation, network connections, registry changes, file modifications

                - configure Sysmon on Windows machine

                ```
                # download sysmon-config.xml from monitor folder
                Sysmon64.exe -accepteula -i sysmon-config.xml
                # output to custom path --- create Logs first under C disk
                wevtutil epl Microsoft-Windows-Sysmon/Operational C:\Logs\sysmon.evtx

                ```

                - add this source inside Windows custom Event:
                ```
                Microsoft-Windows-Sysmon/Operational
                ```

            - Firewall logs
                
                - configured on windows system:

                    inside Windows Defender Firewall Properties, set:

                        - Log dropped packets: Yes

                        - Log successful connections: Yes (optional)

                        - Log file path: %systemroot%\system32\LogFiles\Firewall\pfirewall.log
                            (C:\Windows\System32\LogFiles\Firewall\pfirewall.log)

        

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
            
            - Firewall


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

    - How to edit or change:

        - Search Data Collection Rules (under top search bar or check with resources)

    - How to start:

        - Go to Log Analytics workspace

        - Under Classic

            - Click "Virtual Machines"

            - Choose desired machine and click

            - Click "connect"


- Data Collection or Export:

    - Windows System:

        - After configure DCR, go to specific Virtual Machines

        - Click "Monitoring" and find "Logs"

        - Select the following tables:

            - Event (include all types of windows event logs)
            - DnsEvent
            - SecurityEvent
            - VMConnection

    - Linux System:

        - After configure DCR, go to specific Virtual Machines

        - Click "Monitoring" and find "Logs"

        - Select the following tables:

            - Syslog (search this log directly)
            
            

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