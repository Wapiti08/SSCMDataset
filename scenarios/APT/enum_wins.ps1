Write-Host "[*] Gather Basic System Information"

# Get system information
systeminfo

# Display the current user
whoami

# Get the hostname of the system
hostname

# Display the current username (environment variable equivalent)
$env:USERNAME

Write-Host "[*] List Users & Groups"

# List all users
net user

# List members of the local Administrators group
net localgroup administrators

Write-Host "[*] Network Information"

# Get detailed network information
ipconfig /all

# Display network connections and listening ports
netstat -ano