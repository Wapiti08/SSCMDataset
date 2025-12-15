# NPM Attack Simulation Guide -- Linux / macOS

This guide demonstrates a simulated NPM supply chain attack that shows how malicious packages can collect system information through a two-stage process.

### 1. Prepare Server

- Simulated Normal Behaviour:

    2, 3, 4, 5, 6, 7

- Linux Server:
    ```bash
    # Update system
    sudo apt update && sudo apt upgrade -y

    # Install Node.js (if not already installed) 
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs

    #if above method failed to download - use nvm
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    source ~/.bashrc
    nvm install 20 # to download v20.x.x
    nvm use 20

    # Verify installation
    node --version # node version has been >=16
    npm --version 
    ```

### 2. Configure Attack Server

1. Create project directory:
```bash
sudo mkdir /opt/attack-server
cd /opt/attack-server
```

2. Copy server.js (payload) to the directory and install dependencies:
```bash
sudo npm init -y
sudo npm install fastify @fastify/cors
```

3. Update IP address in server.js:
```bash
# Replace all instances of 10.96.177.36 with your Linux server's IP address
# You can use text editor or sed command:
sudo sed -i 's/10.96.177.36/YOUR.SERVER.IP.HERE/g' server.js
```

4. Start the server:
```bash
# Generate self-signed certificate if needed
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"

# Run server (requires root for port 443)
sudo node server.js
```

### 3. Modify Attack Packages

1. Modify the IP to your server's IP:
```
.
├── audit-ejs-1.7.2
│   ├── main.js
│   └── package.json
├── audit-vue-1.6.2
│   ├── main.js
│   └── package.json
└── server.js
```

2. Extract and modify packages:
```bash
# Update IP addresses
cd audit-ejs-1.7.2/package
# Edit main.js - replace 10.96.177.36 with your server IP
cd ../../

cd audit-vue-1.6.2/package
# Edit main.js - replace 10.96.177.36 with your server IP
cd ../../
```

### 3. Repack Modified Packages

1. For audit-ejs:
```bash

npm pack audit-ejs-1.7.2/
```

2. For audit-vue:
```bash
npm pack audit-vue-1.6.2/
```

### 5. Execute Attack

1. Stage One - Token Retrieval:
```bash
npm install audit-ejs-1.7.2.tgz
# Creates ~/.npm/audit-cache with token
```

2. Stage Two - Payload Execution:
```bash
npm install audit-vue-1.6.2.tgz
# Creates and executes ~/.npm/audit.js
```

### 6. Attack Results

Files created:
- `~/.npm/audit-cache` - Contains token from first stage
- `~/.npm/audit.js` - Contains and executes collection script

### Victim Machine Status
![Victim Machine Status](imgs/victim.png)

### Attack Server Status
![Attack Server Status](imgs/attack_server.png)


### 7. Check Server Logs
```bash
cat /opt/attack-server/logs/system_info.log
```

## Attack Timeline
    (target: host1, attacker: host2)

    - host1 (2025.12.15)

        # start simulate normal behaviour
        ```
        
        ```

