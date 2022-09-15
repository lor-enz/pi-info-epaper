import subprocess


class TechnicalInfo:
    
    local_ip = None

    def __init__(self):
        self.local_ip = f"IP: {subprocess.getoutput('hostname -I')}"
