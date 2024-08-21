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

- office work

- web visit

- remote ssh

- ftp service for file transfer

- open software and call update

- download repository 

- automatic development (pip, compile)

## Factors for Normalization

- idle time

- randomization

## Pre-Installation for Hosts

- office set

- sensitive information storage

    - cache
    - configuration file
    - password text

- python

- software

    Windows (office): firefox, zoom, skype, slack, discord, 1password

    Windows (dev): vs code, filezilla, pip, MobaXterm, discord, 1password

    Linux (dev): vs code, docker, slack, discord, 1password

## Details of Host Configuration

- wins dev

    - IP:

    - Pre-installed Software
    
    - Open Services
    
    - Simulated Behaviours

    - Sensititive Information
        - credentials (.txt, .ini)
        - configuration files (.conf, .ini, .xml)
        - system information


- linux dev

    - IP:

    - Pre-installed Software
    
    - Open Services
    
    - Simulated Behaviours

    - Sensititive Information
        - credentials (.txt, .ini)
        - configuration files (.conf, .ini, .xml)
        - system information


- wins office

    - IP:

    - Pre-installed Software
    
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

- 


## Running Instructions
```
# make sure pyenv has been configured before
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

```