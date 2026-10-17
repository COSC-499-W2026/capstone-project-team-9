
"""
Utility functions that stop the tests and app being run outside of a Docker Container.
Needed to ensure environment parity between developers, CI, etc.
"""
import os
import sys
import textwrap

def docker_guard(program : str, alt_command : str) -> None:
    """
    If a program is running outside Docker, stops it,
    prints a warning and suggests alternate command.
    """
    if os.getenv("RUNNING_IN_DOCKER") != "true":
        print(textwrap.dedent(f"""
            🛑 STOP! You are trying to run {program} on your host machine.
            {program.capitalize()} must be run inside Docker to ensure environment parity.
            👉 Run this instead:
                {alt_command}
        """))
        sys.exit(1)