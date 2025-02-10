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

- ftp service for file transfer (4)

- open software and call update (5)

- download repository (6)

- automatic development (pip, compile) (7)

## Factors for Randomness

- idle time

- randomization

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

- 


## Running Instructions
```
pyenv global 3.10.1
pyenv local 3.10.1
# make sure pyenv has been configured before
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"


```