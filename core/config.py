'''
    define parameters to achieve simulation for normal behaviour
'''


git_reps_list = [
    "https://github.com/ytdl-org/youtube-dl.git",
    "https://github.com/nvbn/thefuck.git",
    "https://github.com/pallets/flask.git",
    "https://github.com/django/django.git",
    "https://github.com/psf/requests.git",
    "https://github.com/psf/cachecontrol.git",
    "https://github.com/sigstore/model-transparency.git",
    "https://github.com/httpie/httpie.git",
    "https://github.com/ansible/ansible.git",
    "https://github.com/psf/requests.git",
    "https://github.com/scikit-learn/scikit-learn.git"

]



web_sites = [
    "https://www.google.com/",
    "https://www.github.com/",
    "https://developer.mozilla.org/en-US/",
    "https://medium.com/",
    "https://www.hackerrank.com/",
    "https://www.youtube.com/",
    "https://uk.linkedin.com/",
    "https://chatgpt.com/",
    "https://www.facebook.com"
]


# ssh host configuration
ssh_hostname = '172.187.202.111'
ssh_ort = 22  # Default SSH port
ssh_username = 'azureofficer'
ssh_password = 'Officelinux01'

# scp remote ssh
scp_hostname = '172.187.202.111'
scp_port = 22  # Default SSH port
scp_username = 'azureofficer'
scp_password = 'Officelinux01'


# file list for copy -- default from wins to linux
local_file_list= ["C:\Users\Newt\Documents\script.py", "C:\Users\Newt\Documents\MyProject", "C:\Users\Newt\Downloads\logs.tar.gz"]
remote_path_list = ["/home/Newt", "/home/Newt/projects", "/opt/logs/"]
