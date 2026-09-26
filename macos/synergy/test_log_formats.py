"""Regression checks for legacy and JSONL Synergy logs (no Karabiner writes)."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from bridge_karabiner import Bridge
from watch_screens import default_log, describe, log_message


class LogFormatsTest(unittest.TestCase):
    def test_bridge_transitions_and_resets_in_both_formats(self):
        messages = [
            ('switch from "mac" to "win"', True),
            ('jump from "win" to "mac"', False),
            ('switch from "mac" to "win"', True),
            ('client "win" has disconnected', False),
            ('switch from "mac" to "win"', True),
            ('stopping core process', False),
            ('entering screen', False),
            ('suspend', False),
        ]
        for structured in (False, True):
            bridge = Bridge('win')
            with patch.object(bridge, 'set_active') as setter:
                for message, expected in messages:
                    line = '[2026-09-27T07:00:00] INFO: ' + message
                    if structured:
                        line = json.dumps({'source': 'core', 'msg': line})
                    bridge.handle_line(line)
                    self.assertEqual(setter.call_args.args, (expected,))
                self.assertEqual(setter.call_count, len(messages))

    def test_structured_description_and_invalid_records(self):
        line = '[2026-09-27T07:00:00] INFO: switch from "mac" to "win"'
        self.assertEqual(describe(line), describe(json.dumps({'msg': line})))
        for record in ('{broken', '{}', '{"msg":null}', '{"msg":42}'):
            self.assertEqual(log_message(record), '')
            self.assertIsNone(describe(record))

    def test_default_prefers_jsonl_over_stale_legacy_log(self):
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            directory = home / 'Library/Logs/Synergy'
            directory.mkdir(parents=True)
            with patch.object(Path, 'home', return_value=home):
                self.assertEqual(default_log(), directory / 'synergy.log')
                (directory / 'synergy.log').touch()
                (directory / 'synergy.jsonl').touch()
                self.assertEqual(default_log(), directory / 'synergy.jsonl')


if __name__ == '__main__':
    unittest.main()
