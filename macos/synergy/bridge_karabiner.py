#!/usr/bin/env python3
"""Enable the Synergy IME rule only after a live transition to the target PC."""

import argparse
import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
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
        logging.info('Karabiner: ' + ('Windows用IMEルール ON' if active else '通常ルール（Windows用 OFF）'))

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
    parser.add_argument('--service-log', type=Path, help='容量制限付きの監視ログ')
    args = parser.parse_args()
    handlers = None
    if args.service_log:
        args.service_log.parent.mkdir(parents=True, exist_ok=True)
        handlers = [RotatingFileHandler(args.service_log, maxBytes=1024 * 1024,
                                        backupCount=3, encoding='utf-8')]
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format='%(asctime)s %(levelname)s %(message)s')
    if not CLI.is_file():
        raise RuntimeError(f'Karabiner CLIが見つかりません: {CLI}')
    bridge = Bridge(args.target)
    if args.reset:
        bridge.reset()
        return
    lock_path = Path(tempfile.gettempdir()) / f'customenter-synergy-{os.getuid()}.lock'
    with lock_path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('連携スクリプトはすでに動作中です。先に既存の監視を終了してください。')
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            signal.signal(sig, interrupt)
        try:
            bridge.reset()
            logging.info(f'対象PC: {args.target}。Macから対象PCへ一度移動すると有効になります。')
            watch(args.log.expanduser(), seconds=0,
                  on_line=bridge.handle_line, on_reset=bridge.reset)
        except KeyboardInterrupt:
            logging.info('連携を終了します。')
        finally:
            # Avoid interrupting the cleanup with a second Ctrl+C.
            for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                signal.signal(sig, signal.SIG_IGN)
            bridge.set_active(False, force=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        logging.exception('連携監視が停止しました。')
        raise SystemExit(1)
