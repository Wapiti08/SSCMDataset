import paramiko
from scp import SCPClient

def create_ssh_client(hostname, port, username, password):
    ''' create and return a SSH client connected to the specified server
    
    '''
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)
    return client


def scp_copy_file(hostname, port, username, password, local_file, remote_path):
    ''' simulate the scp action to copy data between hosts with python script
    
    '''
    try:
        # Create the SSH client
        ssh_client = create_ssh_client(hostname, port, username, password)
        
        # Create an SCP client from the SSH connection
        with SCPClient(ssh_client.get_transport()) as scp:
            # Copy the file
            scp.put(local_file, remote_path)
            print(f"File '{local_file}' successfully copied to '{remote_path}' on '{hostname}'")
        
    except Exception as e:
        print(f"An error occurred while copying the file: {e}")
    
    finally:
        # Close the SSH connection
        ssh_client.close()

if __name__ == "__main__":

    # Example usage
    hostname = 'your.remote.server.com'
    port = 22  # Default SSH port
    username = 'your_username'
    password = 'your_password'
    local_file = '/path/to/local/file.txt'
    remote_path = '/path/to/remote/destination/'

    scp_copy_file(hostname, port, username, password, local_file, remote_path)