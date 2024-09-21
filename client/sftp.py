import paramiko


def sftp_session(host, port, username, password):
    transport = paramiko.Transport((host, port))
    transport.banner_timeout = 200
    transport.connect(None, username, password)
    return paramiko.SFTPClient.from_transport(transport), transport
