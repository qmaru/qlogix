import subprocess

from qlogix.logutil import get_logger, log_external_call
from qlogix.source.base import Source, SourceBaseContent, SourceType

logger = get_logger(__name__)


class CommandSource(Source):
    def __init__(self, command: str, shell_type: str = "default", source_name: str | None = None):
        self.command = command
        self.shell_type = shell_type
        self.source_name = source_name

    def fetch(self) -> list[SourceBaseContent]:
        shell_map = {
            "powershell": ["powershell", "-NoProfile", "-Command", self.command],
            "cmd": ["cmd", "/c", self.command],
            "bash": ["bash", "-c", self.command],
        }

        if self.shell_type == "default":
            cmd = self.command
            shell = True
        else:
            cmd = shell_map[self.shell_type]
            shell = False

        result = log_external_call(
            logger,
            "subprocess.run",
            lambda: subprocess.run(cmd, shell=shell, capture_output=True, text=True),
            source=self.source_name,
            shell_type=self.shell_type,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return [
            SourceBaseContent(
                source=SourceType.COMMAND, source_name=self.source_name, message=line.strip()
            )
            for line in result.stdout.splitlines()
            if line.strip()
        ]
