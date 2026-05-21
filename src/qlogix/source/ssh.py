import getpass
from urllib.parse import urlparse

import paramiko
from pydantic import BaseModel, Field

from qlogix.source.base import Source


class SSHConfig(BaseModel):
    host: str = Field(..., description="SSH server hostname or IP address")
    port: int = Field(22, description="SSH server port (default: 22)")
    username: str = Field(..., description="SSH username")
    password: str | None = Field(..., description="SSH password")
    private_key: str | None = Field(None, description="Path to SSH private key file (optional)")


class SSHSource(Source):
    def __init__(self, target: str):
        config = parse_ssh_target(target)

        self.host = config[1].host
        self.port = config[1].port
        self.username = config[1].username
        self.password = config[1].password
        self.private_key = config[1].private_key
        self.log_path = config[0]

    def __ssh_connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.private_key:
            key = paramiko.RSAKey.from_private_key_file(self.private_key)
            client.connect(self.host, username=self.username, pkey=key)
        else:
            client.connect(self.host, username=self.username, password=self.password)
        return client

    def fetch(self) -> list[dict]:
        # ssh user@server:/var/log/app.log
        client = self.__ssh_connect()
        stdin, stdout, stderr = client.exec_command(f"cat {self.log_path}")
        lines = stdout.readlines()
        client.close()
        return [{"source": "ssh", "message": line.strip()} for line in lines]


def parse_ssh_target(
    target: str,
    password: str | None = None,
    key: str | None = None,
) -> tuple[str, SSHConfig]:
    uri = urlparse(target)

    if uri.scheme != "ssh":
        raise ValueError("expected: ssh://user@host/path")

    if not uri.hostname:
        raise ValueError("missing ssh host")

    if not uri.username:
        raise ValueError("missing ssh username")

    if not uri.path:
        raise ValueError("missing remote log path")

    if not key and not password:
        password = getpass.getpass(f"{uri.username}@{uri.hostname} password: ")

    if not password and not key:
        raise ValueError("must provide either password or private key for ssh authentication")

    config = SSHConfig(
        host=uri.hostname,
        port=uri.port or 22,
        username=uri.username,
        password=password,
        private_key=key,
    )

    return uri.path, config
