#!/usr/bin/env python3
"""Read-only Synergy screen-transition monitor; standard library only."""

import argparse
from contextlib import closing
import os
import logging
from pathlib import Path
import re
import select
import time


TRANSITION = re.compile(r'\b(switch|jump) from "([^"]+)" to "([^"]+)"')
TIMESTAMP = re.compile(r'\[(\d{4}-\d{2}-\d{2}T[^\]]+)\]')


def describe(line):
    match = TRANSITION.search(line)
    if not match:
        return None
    kind, origin, destination = match.groups()
    timestamp = TIMESTAMP.search(line)
    logged_at = timestamp.group(1) if timestamp else '時刻なし'
    return f'ログ {logged_at} | {origin} → {destination} ({kind})'


def watch(path, seconds, on_line=None, on_reset=None):
    deadline = time.monotonic() + seconds if seconds else None
    stream = None
    identity = None
    pending = b''
    startup = True
    missing = False
    logging.info(f'監視対象: {path}')
    logging.info('現在の操作先は未判定。起動後の画面移動を検知します。')
    logging.info('MacとWindowsの間でマウスを往復してください。終了: Ctrl+C')

    def register(queue, fd):
        event = select.kevent(
            fd, filter=select.KQ_FILTER_VNODE,
            flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
            fflags=(select.KQ_NOTE_WRITE | select.KQ_NOTE_EXTEND |
                    select.KQ_NOTE_RENAME | select.KQ_NOTE_DELETE |
                    select.KQ_NOTE_REVOKE))
        queue.control([event], 0, 0)

    def drain():
        nonlocal pending
        while stream is not None:
            chunk = stream.read(65536)
            if not chunk:
                break
            pending += chunk
            lines = pending.split(b'\n')
            pending = lines.pop()
            for raw in lines:
                line = raw.decode('utf-8', errors='replace')
                if on_line:
                    on_line(line)
                result = describe(line)
                if result:
                    detected = time.strftime('%H:%M:%S')
                    logging.info(f'検知 {detected} | {result}')

    # Watch the directory too: a rotated log is a different inode, and may
    # appear some time after the old file has been renamed/deleted.
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        with closing(select.kqueue()) as queue:
            register(queue, directory_fd)
            while deadline is None or time.monotonic() < deadline:
                try:
                    stat = path.stat()
                except FileNotFoundError:
                    stat = None
                if stat is None:
                    if not missing:
                        logging.info('ログが見つかりません。作成通知を待機します。')
                    missing = True
                    drain()
                    if on_reset:
                        on_reset()
                else:
                    current_identity = (stat.st_dev, stat.st_ino)
                    if stream is None or identity != current_identity:
                        drain()
                        try:
                            replacement = path.open('rb', buffering=0)
                        except FileNotFoundError:
                            # A concurrent rename has already queued a directory event.
                            replacement = None
                        if replacement is not None:
                            if on_reset:
                                on_reset()
                            if stream is not None:
                                stream.close()  # Closing also removes its kevent.
                            stream = replacement
                            opened = os.fstat(stream.fileno())
                            identity = (opened.st_dev, opened.st_ino)
                            pending = b''
                            register(queue, stream.fileno())
                            if startup:
                                stream.seek(0, os.SEEK_END)
                            else:
                                logging.info('新しいログを検知。先頭から監視します。')
                    if stream is not None:
                        if os.fstat(stream.fileno()).st_size < stream.tell():
                            if on_reset:
                                on_reset()
                            stream.seek(0)
                            pending = b''
                            logging.info('ログの切り詰めを検知。先頭から監視します。')
                        drain()
                    missing = False
                if startup:
                    startup = False
                    logging.info('監視開始（kqueue方式・定期ポーリングなし）')
                timeout = None if deadline is None else max(0, deadline - time.monotonic())
                queue.control(None, 8, timeout)
    finally:
        if stream is not None:
            stream.close()
        os.close(directory_fd)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path,
                        default=Path.home() / 'Library/Logs/Synergy/synergy.log')
    parser.add_argument('--seconds', type=float, default=0,
                        help='指定秒数で終了。省略時はCtrl+Cまで監視')
    args = parser.parse_args()
    if args.seconds < 0:
        parser.error('--seconds must be nonnegative')
    try:
        watch(args.log.expanduser(), seconds=args.seconds)
    except KeyboardInterrupt:
        logging.info('\n監視を終了しました。')


if __name__ == '__main__':
    main()
