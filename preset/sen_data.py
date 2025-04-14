'''
 # @ Create Time: 2024-08-21 11:58:12
 # @ Modified time: 2024-08-21 11:58:14
 # @ Description: pre-download financial/annual reports to office host
 '''

import os
import requests
import zipfile
from pathlib import Path

# set downlaod location
download_to = "Downloads"

# get user's home directory and resolve full path
home = Path.home()
download_dir = Path(home).joinpath(download_to)

# ensure the folder exists
os.makedirs(download_dir, exist_ok=True)

# define list of files to download
files_to_download = [
    "https://www.sec.gov/files/dera/data/financial-statement-data-sets/2023q4.zip",
    "https://www.sec.gov/files/dera/data/financial-statement-data-sets/2015q4.zip",
    "https://www.nestle.com/sites/default/files/2024-02/2023-annual-review-en.pdf",
    "https://www.credit-suisse.com/media/assets/corporate/docs/about-us/investor-relations/financial-disclosures/financial-reports/csag-ar-2023-en.pdf"
]

# download and unzip if necessary
for url in files_to_download:
    filename = url.split("/")[-1]
    file_path = Path(download_dir).joinpath(filename).as_posix()

    print(f"Downloading: {filename}")
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Saved to: {file_path}")
    
        # if it's a zip file, unzip it
        if filename.endswith(".zip"):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(Path(download_dir).joinpath(filename.replace(".zip", "")))
                print(f"unzipped to: {download_dir/filename.replace(".zip", "")}")
            except zipfile.BadZipFile:
                print("Failed to unzip: Bad Zip file")
    
    else:
        print(f"Failed to download (status code: {response.status_code})")


