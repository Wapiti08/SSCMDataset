# Display current user privileges
whoami /priv

Write-Host "[*] Scanning for Internal Network Devices"

# Run arp -a to list devices in the local network
arp -a

# Loop through IPs 192.168.1.1 to 192.168.1.254 and ping each one
for ($i = 1; $i -le 254; $i++) {
    $ip = "192.168.1.$i"
    $pingResult = Test-Connection -ComputerName $ip -Count 1 -Quiet
    if ($pingResult) {
        Write-Host "Reply from $ip"
    }
}

Write-Host "[*] Checking valid credentials"

# List stored credentials using cmdkey
cmdkey /list