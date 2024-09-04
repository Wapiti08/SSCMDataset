import socket
import platform
import psutil
import json
import os

def get_system_info():
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

def save_system_info_to_file(file_path):
    system_info = get_system_info()
    
    with open(file_path, 'w') as file:
        json.dump(system_info, file, indent=4)

if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    file_path = os.path.join(script_dir, "system_info.json")
    save_system_info_to_file(file_path)
    print(f"System information saved to {file_path}")