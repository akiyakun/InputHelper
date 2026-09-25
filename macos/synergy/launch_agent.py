#!/usr/bin/env python3
"""Generate a LaunchAgent for the current checkout and Python interpreter."""

from pathlib import Path
import plistlib
import sys
import tempfile


LABEL = 'local.inputhelper.synergy-ime'


def configuration():
    directory = Path(__file__).resolve().parent
    return {
        'Label': LABEL,
        'ProgramArguments': [
            sys.executable, '-B', '-u', str(directory / 'bridge_karabiner.py'),
            '--service-log', str(Path.home() / 'Library/Logs/InputHelper/synergy-ime.log'),
        ],
        'WorkingDirectory': str(directory),
        'RunAtLoad': True,
        'KeepAlive': True,
        'ThrottleInterval': 15,
        'ExitTimeOut': 15,
        'LimitLoadToSessionType': 'Aqua',
        # Match manual invocations so both use the same singleton lock.
        'EnvironmentVariables': {'TMPDIR': tempfile.gettempdir()},
        'StandardOutPath': '/dev/null',
        'StandardErrorPath': '/dev/null',
    }


if __name__ == '__main__':
    sys.stdout.buffer.write(plistlib.dumps(configuration()))
