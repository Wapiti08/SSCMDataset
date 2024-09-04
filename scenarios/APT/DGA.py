'''
 # @ Author: Newt Tan
 # @ Create Time: 2024-09-04 11:09:58
 # @ Modified by: Newt Tan
 # @ Modified time: 2024-09-04 11:29:21
 # @ Description: implement basic DGA function to update domain every 30 minutes
 '''

import hashlib
import time

def generate_domain(seed, tld=".com"):
    timestamp = int(time.time()) // (30 * 60)
    hash_input = f"{seed}{timestamp}".encode()
    domain_hash = hashlib.md5(hash_input).hexdigest()
    domain = f"{domain_hash[:9]}{tld}"
    return domain


if __name__ == "__main__":
    seed = "JURWJDWJraeaR"
    for _ in range(10):
        print(generate_domain(seed))