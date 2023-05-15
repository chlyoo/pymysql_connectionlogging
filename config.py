import paramiko


ssh_config = {
    'username': '',
    'host': '',
    'port': 22,
    'ssh_key': paramiko.RSAKey.from_private_key_file(''),
    'local_port': 3307
}

connection_info = {
    'username': '',
    'password': '',
    'host': '',
    'database': '',
    'port': 3306,
    'ssh_config': ssh_config
}
