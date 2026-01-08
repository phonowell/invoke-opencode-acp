#!/usr/bin/env python3
"""Unit tests for acp_client.py"""
import unittest
from unittest.mock import Mock, patch
import json
import re
from acp_client import ACPClient, ACPError, ACPTimeoutError

class TestACPClient(unittest.TestCase):
    def setUp(self):
        self.client = ACPClient(verbose=False)

    def test_init(self):
        client = ACPClient(verbose=True)
        self.assertTrue(client.verbose)
        self.assertIsNone(client.proc)

    def test_init_default(self):
        client = ACPClient()
        self.assertFalse(client.verbose)

    def test_send_request_no_process(self):
        with self.assertRaises(ACPError) as ctx:
            self.client.send_request(1, "test", {})
        self.assertIn("Process not started", str(ctx.exception))

    @patch('subprocess.Popen')
    def test_send_request_success(self, mock_popen):
        mock_proc = Mock()
        mock_stdin = Mock()
        mock_proc.stdin = mock_stdin
        self.client.proc = mock_proc

        self.client.send_request(1, "initialize", {"protocolVersion": 1})

        mock_stdin.write.assert_called_once()
        written = mock_stdin.write.call_args[0][0]
        data = json.loads(written)

        self.assertEqual(data["jsonrpc"], "2.0")
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["method"], "initialize")
        self.assertEqual(data["params"]["protocolVersion"], 1)
        mock_stdin.flush.assert_called_once()

    @patch('subprocess.Popen')
    def test_send_request_broken_pipe(self, mock_popen):
        mock_proc = Mock()
        mock_proc.stdin.write.side_effect = BrokenPipeError()
        self.client.proc = mock_proc

        with self.assertRaises(ACPError) as ctx:
            self.client.send_request(1, "test", {})
        self.assertIn("Failed to send", str(ctx.exception))

    @patch('subprocess.Popen')
    def test_execute_task_opencode_not_found(self, mock_popen):
        mock_popen.side_effect = FileNotFoundError()

        with self.assertRaises(ACPError) as ctx:
            self.client.execute_task("/tmp", "test task")
        self.assertIn("opencode command not found", str(ctx.exception))

    def test_thinking_filter_regex(self):
        """Test thinking filter logic"""
        text = "<thinking>分析中</thinking>输出结果"
        filtered = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        self.assertEqual(filtered, "输出结果")

    def test_thinking_filter_multiline(self):
        """Test thinking filter with multiline content"""
        text = "前文<thinking>\n多行\n分析\n</thinking>后文"
        filtered = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        self.assertEqual(filtered, "前文后文")

    def test_thinking_filter_multiple(self):
        """Test multiple thinking blocks"""
        text = "a<thinking>1</thinking>b<thinking>2</thinking>c"
        filtered = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        self.assertEqual(filtered, "abc")

class TestACPExceptions(unittest.TestCase):
    def test_acp_error(self):
        err = ACPError("test error")
        self.assertEqual(str(err), "test error")
        self.assertIsInstance(err, Exception)

    def test_acp_timeout_error(self):
        err = ACPTimeoutError("Task timeout")
        self.assertIsInstance(err, ACPError)
        self.assertEqual(str(err), "Task timeout")

    def test_acp_timeout_inheritance(self):
        """Test that ACPTimeoutError can be caught as ACPError"""
        try:
            raise ACPTimeoutError("timeout")
        except ACPError as e:
            self.assertIn("timeout", str(e))

if __name__ == '__main__':
    unittest.main()
