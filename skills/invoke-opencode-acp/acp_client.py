#!/usr/bin/env python3
"""OpenCode ACP client for delegating tasks to subagent (saves main agent tokens)"""
import subprocess
import json
import time
import sys
import select
import argparse
import re
from typing import Tuple

class ACPError(Exception):
    """ACP protocol errors"""
    pass

class ACPTimeoutError(ACPError):
    """Task timeout errors"""
    pass

class ACPClient:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.proc = None

    def send_request(self, req_id: int, method: str, params: dict):
        if not self.proc:
            raise ACPError("Process not started")
        request = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
        if self.verbose:
            print(f">>> {request}", file=sys.stderr)
        try:
            self.proc.stdin.write(request + '\n')
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            raise ACPError(f"Failed to send: {e}")
    def execute_task(self, cwd: str, task: str, timeout: float = 1800) -> Tuple[str, int]:
        try:
            self.proc = subprocess.Popen(
                ['opencode', 'acp'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
        except FileNotFoundError:
            raise ACPError("opencode command not found")
        except Exception as e:
            raise ACPError(f"Failed to start: {e}")

        output_chunks = []

        try:
            # Initialize
            self.send_request(1, "initialize", {
                "protocolVersion": 1,
                "capabilities": {},
                "clientInfo": {"name": "claude-code", "version": "1.0"}
            })

            # Read init responses (discard)
            start = time.time()
            while time.time() - start < 3:
                try:
                    ready, _, _ = select.select([self.proc.stdout], [], [], 0.1)
                except (ValueError, OSError):
                    break
                if ready:
                    line = self.proc.stdout.readline().strip()
                    if line and self.verbose:
                        print(f"<<< {line}", file=sys.stderr)
                time.sleep(0.05)

            # Create session
            self.send_request(2, "session/new", {"cwd": cwd, "mcpServers": []})

            # Read session responses
            session_id = None
            start = time.time()
            while time.time() - start < 3:
                try:
                    ready, _, _ = select.select([self.proc.stdout], [], [], 0.1)
                except (ValueError, OSError):
                    break
                if ready:
                    line = self.proc.stdout.readline().strip()
                    if line:
                        if self.verbose:
                            print(f"<<< {line}", file=sys.stderr)
                        try:
                            data = json.loads(line)
                            if "error" in data:
                                err = data["error"]
                                raise ACPError(f"Protocol error [{err.get('code', -1)}]: {err.get('message', 'Unknown')}")
                            if "result" in data and "sessionId" in data.get("result", {}):
                                session_id = data["result"]["sessionId"]
                                break
                        except json.JSONDecodeError:
                            pass
                time.sleep(0.05)

            if not session_id:
                raise ACPError("Failed to create session")

            # Execute task with injected constraints
            task_with_constraints = f"""{task}

IMPORTANT: Keep output concise with summary-first approach. Show key results only, no detailed breakdowns or verbose reasoning."""

            self.send_request(3, "session/prompt", {
                "sessionId": session_id,
                "prompt": [{"type": "text", "text": task_with_constraints}]
            })

            # Read task responses
            start_time = time.time()
            task_complete = False
            response_count = 0

            while time.time() - start_time < timeout:
                try:
                    line = self.proc.stdout.readline().strip()
                    if line:
                        if self.verbose:
                            print(f"<<< {line}", file=sys.stderr)
                        try:
                            data = json.loads(line)
                            response_count += 1

                            # Collect agent message chunks (filter thinking)
                            if data.get("method") == "session/update":
                                update = data.get("params", {}).get("update", {})
                                if update.get("sessionUpdate") == "agent_message_chunk":
                                    content = update.get("content", {})
                                    if content.get("type") == "text":
                                        text = content.get("text", "")
                                        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
                                        if text.strip():
                                            output_chunks.append(text)

                            # Check completion
                            if data.get("result", {}).get("stopReason") == "end_turn":
                                task_complete = True
                                break
                        except json.JSONDecodeError:
                            pass
                except Exception:
                    break

            if not task_complete and time.time() - start_time >= timeout:
                raise ACPTimeoutError(f"Task timeout after {timeout}s")

            return "".join(output_chunks), response_count

        finally:
            if self.proc:
                self.proc.stdin.close()
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
def main():
    parser = argparse.ArgumentParser(description="OpenCode ACP Protocol Client")
    parser.add_argument("cwd", help="Working directory")
    parser.add_argument("task", help="Task description")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show protocol messages (stderr)")
    parser.add_argument("-t", "--timeout", type=float, default=1800, help="Timeout in seconds (default: 1800)")
    parser.add_argument("-o", "--output", required=True, help="Output file (REQUIRED)")

    args = parser.parse_args()

    client = ACPClient(verbose=args.verbose)

    try:
        final_output, _ = client.execute_task(args.cwd, args.task, args.timeout)

        with open(args.output, 'w') as f:
            f.write(final_output)

        print("✓ Subagent task completed")
        sys.exit(0)

    except ACPTimeoutError as e:
        print(f"✗ Timeout: {e}", file=sys.stderr)
        sys.exit(2)
    except ACPError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(4)

if __name__ == "__main__":
    main()
