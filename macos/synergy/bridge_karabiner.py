#!/usr/bin/env python3
"""Enable the Synergy IME rule only after a live transition to the target PC."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile

from watch_screens import TRANSITION, watch


CLI = Path('/Library/Application Support/org.pqrs/Karabiner-Elements/bin/karabiner_cli')
VARIABLE = 'customenter_synergy_windows'
DISCONNECT = re.compile(r'client "([^"]+)" has disconnected', re.I)
STOP = re.compile(r'stopping core process|stopped core process|server is dead|\bsuspend\b', re.I)


class Bridge:
    def __init__(self, target, cli=CLI):
        self.target = target.casefold()
        self.cli = cli
        self.active = None

    def set_active(self, active, force=False):
        if self.active == active and not force:
            return
        result = subprocess.run(
            [str(self.cli), '--set-variables', json.dumps({VARIABLE: int(active)})],
            check=True, timeout=5, capture_output=True, text=True,
        )
        # Some CLI failures are printed even when the exit status is zero.
        output = (result.stdout + result.stderr).strip()
        if 'error' in output.casefold():
            raise RuntimeError(f'Karabinerへの設定に失敗しました: {output}')
        self.active = active
        print('Karabiner: ' + ('Windows用IMEルール ON' if active else '通常ルール（Windows用 OFF）'),
              flush=True)

    def reset(self):
        self.set_active(False)

    def handle_line(self, line):
        transition = TRANSITION.search(line)
        if transition:
            self.set_active(transition.group(3).casefold() == self.target)
            return
        disconnected = DISCONNECT.search(line)
        if (disconnected and disconnected.group(1).casefold() == self.target) or STOP.search(line):
            self.reset()
        elif re.search(r'\bentering screen\b', line):
            # In the Mac server's log, this means input returned to the Mac.
            self.reset()


def interrupt(signum, frame):
    raise KeyboardInterrupt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path,
                        default=Path.home() / 'Library/Logs/Synergy/synergy.log')
    parser.add_argument('--target', default='s500plus-27441e4d')
    parser.add_argument('--reset', action='store_true', help='監視せず、Windows用ルールをOFFにする')
    args = parser.parse_args()
    if not CLI.is_file():
        parser.error(f'Karabiner CLIが見つかりません: {CLI}')
    bridge = Bridge(args.target)
    if args.reset:
        bridge.reset()
        return
    lock_path = Path(tempfile.gettempdir()) / f'customenter-synergy-{os.getuid()}.lock'
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error('連携スクリプトはすでに動作中です。先に既存の監視を終了してください。')
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, interrupt)
        try:
            bridge.reset()
            print(f'対象PC: {args.target}。Macから対象PCへ一度移動すると有効になります。', flush=True)
            watch(args.log.expanduser(), seconds=0,
                  on_line=bridge.handle_line, on_reset=bridge.reset)
        except KeyboardInterrupt:
            print('\n連携を終了します。', flush=True)
        finally:
            # Avoid interrupting the cleanup with a second Ctrl+C.
            for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                signal.signal(sig, signal.SIG_IGN)
            bridge.set_active(False, force=True)


if __name__ == '__main__':
    main()
