import paramiko
import os
from concurrent.futures import ThreadPoolExecutor

# 
pub_keys_folder = '/home/kali/.ssh'

# Baca daftar pengguna dari file
with open('users.txt', 'r') as f:
    users = [line.strip().split(':') for line in f if line.strip()]

# Baca daftar server dari file
with open('servers.txt', 'r') as f:
    servers = [line.strip() for line in f if line.strip()]

def distribute_key_and_create_user(server):
    try:
        print(f"Connecting to {server}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, username='muezza', password='Edward1456#')
        
        for user, password in users:
            # ssh client
            pub_key_path = os.path.join(pub_keys_folder, f'{user}.pub')
            
            if not os.path.exists(pub_key_path):
                print(f"Public key for {user} not found. Skipping.")
                continue
            
            # public ssh_key
            with open(pub_key_path, 'r') as f:
                pub_key = f.read().strip()
            
            # create user:pas
            client.exec_command(f'sudo useradd -m -s /bin/bash {user}')
            client.exec_command(f'echo "{user}:{password}" | sudo chpasswd')
            
            # user direc
            client.exec_command(f'sudo -u {user} mkdir -p /home/{user}/.ssh')
            
            # add auth new user
            cmd = f'echo "{pub_key}" | sudo tee -a /home/{user}/.ssh/authorized_keys'
            client.exec_command(cmd)
            
            client.exec_command(f'sudo chown -R {user}:{user} /home/{user}/.ssh')
            client.exec_command(f'sudo chmod 700 /home/{user}/.ssh')
            client.exec_command(f'sudo chmod 600 /home/{user}/.ssh/authorized_keys')

            # Vrfy
            stdin, stdout, stderr = client.exec_command(f'sudo cat /home/{user}/.ssh/authorized_keys')
            authorized_keys = stdout.read().decode('utf-8')
            if pub_key in authorized_keys:
                print(f"SSH key successfully added for {user} on {server}")
            else:
                print(f"Failed to add SSH key for {user} on {server}")

        client.close()
    except Exception as e:
        print(f"Failed to connect to {server}: {e}")

# limit dari worker
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(distribute_key_and_create_user, servers)
