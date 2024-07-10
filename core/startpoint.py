''' 
    according to system type to download compatible tools

# '''
# import platform
# import subprocess
# from pathlib import Path
# import zipfile

# plat_info = platform.platform()

# # webdriver_mac = "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/mac-arm64/chromedriver-mac-arm64.zip"
# # webdriver_linux = "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip"
# # webdriver_windows = "https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/win64/chromedriver-win64.zip"


# def download_webdriver(os_type, output_path='.'):
#     if os_type.startswith("mac"):
#         result = subprocess.run(['wget', "-P", output_path, webdriver_mac], capture_output=True, text=True)

#     elif os_type.startswith("Windows"):
#         result = subprocess.run(['wget', "-P", output_path, webdriver_windows], capture_output=True, text=True)

#     elif os_type.startswith("Linux"):
#         result = subprocess.run(['wget', "-P", output_path, webdriver_linux], capture_output=True, text=True)

#     else:
#         print("the os type is wrong")
#         exit()
    
#     if result.returncode == 0:
#         print("Download successful")
#         # unzip the file

#     else:
#         print("Download Failed")
#         print('STEDER:', result.stderr)

# def find_zip_files(directory='.'):
#     # Construct the search pattern for .zip files
#     search_pattern = Path(directory)
#     # Use glob to find all matching files
#     zip_files = list(search_pattern.glob("*.zip"))
#     return zip_files

# def unzip_file(zip_file, extract_to='.'):
#     with zipfile.ZipFile(zip_file, 'r') as zip_ref:
#         zip_ref.extractall(extract_to)
#         print(f"zip file {zip_file} successfully to {extract_to}")

if __name__ == "__main__":
    # download_webdriver(plat_info)
    # cur_path = Path.cwd().as_posix()
    # zip_files = find_zip_files(cur_path)
    # for zip_file in zip_files:
    #     unzip_file(zip_file, cur_path)