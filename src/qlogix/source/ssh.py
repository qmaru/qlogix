import getpass
import shlex
from urllib.parse import urlparse

import paramiko
from pydantic import BaseModel, Field

from qlogix.logutil import get_logger, log_external_call
from qlogix.source.base import Source, SourceBaseContent, SourceType

logger = get_logger(__name__)


class SSHConfig(BaseModel):
    host: str = Field(..., description="SSH server hostname or IP address")
    port: int = Field(22, description="SSH server port (default: 22)")
    username: str = Field(..., description="SSH username")
    password: str | None = Field(None, description="SSH password")
    private_key: str | None = Field(None, description="Path to SSH private key")


class SSHSource(Source):
    def __init__(
        self,
        target: str,
        password: str | None = None,
        key: str | None = None,
        command: str | None = None,
        source_name: str | None = None,
    ):
        config = parse_ssh_target(target, password, key, command)

        self.log_path = config[0]
        self.ssh_config = config[1]
        self.command = command
        self.source_name = source_name

    def __ssh_connect(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.ssh_config.private_key:
            client.connect(
                self.ssh_config.host,
                port=self.ssh_config.port,
                username=self.ssh_config.username,
                key_filename=self.ssh_config.private_key,
                look_for_keys=False,
                allow_agent=False,
            )
        else:
            client.connect(
                self.ssh_config.host,
                port=self.ssh_config.port,
                username=self.ssh_config.username,
                password=self.ssh_config.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10,
                auth_timeout=10,
                banner_timeout=10,
            )
        return client

    def __run_remote(self, client) -> list[str]:
        cmd = self.command or f"cat {shlex.quote(self.log_path)}"
        stdin, stdout, stderr = client.exec_command(cmd)

        exit_code = stdout.channel.recv_exit_status()
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace").strip()

        if exit_code != 0:
            raise RuntimeError(
                f"ssh command failed: exit_code={exit_code}, command={cmd!r}, stderr={err!r}"
            )

        return out.splitlines()

    def fetch(self) -> list[SourceBaseContent]:
        with self.__ssh_connect() as client:
            lines = log_external_call(
                logger,
                "ssh.exec_command",
                lambda: self.__run_remote(client),
                source=self.source_name,
                host=self.ssh_config.host,
                path=self.log_path,
                command=self.command,
            )

        return [
            SourceBaseContent(source=SourceType.SSH, source_name=self.source_name, message=line)
            for line in lines
        ]


def parse_ssh_target(
    target: str,
    password: str | None = None,
    key: str | None = None,
    command: str | None = None,
) -> tuple[str, SSHConfig]:
    uri = urlparse(target)

    if uri.scheme != "ssh":
        raise ValueError("expected: ssh://user@host/path")

    if not uri.hostname:
        raise ValueError("missing ssh host")

    if not uri.username:
        raise ValueError("missing ssh username")

    if not command and not uri.path:
        raise ValueError("missing remote log path")

    if not key and not password:
        password = getpass.getpass(f"{uri.username}@{uri.hostname} password: ")

    config = SSHConfig(
        host=uri.hostname,
        port=uri.port or 22,
        username=uri.username,
        password=password,
        private_key=key,
    )

    return uri.path or "", config
