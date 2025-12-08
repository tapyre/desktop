from abstractions.plugin import Plugin
import subprocess

class CommandPlugin(Plugin):
    def __init__(self):
        self.prefix = "cmd"
        self.name = "command"
        self.prompt = "Executes a shell command and returns the output."

    def run(self, text: str) -> str:
        try:
            result = subprocess.run(
                text,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        except FileNotFoundError:
            return f"Error: Command not found."
