import subprocess

from qlogix.source.base import Source


class CommandSource(Source):
    def __init__(
        self,
        command: str,
        shell_type: str = "default",
    ):
        self.command = command
        self.shell_type = shell_type

    def fetch(self) -> list[dict]:
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

        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        return [
            {"source": "command", "message": line.strip()}
            for line in result.stdout.splitlines()
            if line.strip()
        ]
