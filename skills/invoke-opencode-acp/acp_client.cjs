#!/usr/bin/env node
/** OpenCode ACP client for delegating tasks to subagent (saves main agent tokens) */
const { spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');

class ACPError extends Error {
	constructor(message) {
		super(message);
		this.name = 'ACPError';
	}
}

class ACPTimeoutError extends ACPError {
	constructor(message) {
		super(message);
		this.name = 'ACPTimeoutError';
	}
}

class ACPClient {
	constructor(verbose = false) {
		this.verbose = verbose;
		this.proc = null;
	}

	send_request(req_id, method, params) {
		if (!this.proc) throw new ACPError('Process not started');
		const request = JSON.stringify({ jsonrpc: '2.0', id: req_id, method, params });
		if (this.verbose) console.error(`>>> ${request}`);
		if (!this.proc.stdin.write(request + '\n')) {
			throw new ACPError('Failed to send: stdin buffer full');
		}
	}

	async execute_task(cwd, task, timeout = 1800) {
		try {
			this.proc = spawn('opencode', ['acp'], { stdio: ['pipe', 'pipe', 'pipe'], shell: false });
		} catch (e) {
			throw new ACPError(e.code === 'ENOENT' ? 'opencode command not found' : `Failed to start: ${e.message}`);
		}

		const output_chunks = [];
		const rl = readline.createInterface({ input: this.proc.stdout, crlfDelay: Infinity });
		const proc = this.proc;
		const SESSION_TIMEOUT = 10000;

		return new Promise((resolve, reject) => {
			let done = false;
			let session_id = null;
			let session_timer = null;

			const finish = (err, result) => {
				if (done) return;
				done = true;
				clearTimeout(session_timer);
				clearTimeout(task_timer);
				rl.close();
				try {
					proc.stdin.end();
					proc.kill();
				} catch (e) {}
				if (err) reject(err);
				else resolve(result);
			};

			const task_timer = setTimeout(() => {
				finish(new ACPTimeoutError(`Task timeout after ${timeout}s`));
			}, timeout * 1000);

			this.proc.on('error', (err) => finish(new ACPError(`Process error: ${err.message}`)));
			this.proc.on('close', (code) => finish(new ACPError(`Process exited early with code ${code}`)));
			this.proc.stderr.on('data', (data) => { if (this.verbose) process.stderr.write(data); });

			rl.on('line', (line) => {
				line = line.trim();
				if (!line) return;
				if (this.verbose) console.error(`<<< ${line}`);

				try {
					const data = JSON.parse(line);

					if (data.error) {
						return finish(new ACPError(`Protocol error [${data.error.code || -1}]: ${data.error.message || 'Unknown'}`));
					}

					if (data.result?.sessionId && !session_id) {
						session_id = data.result.sessionId;
						clearTimeout(session_timer);
						try {
							this.send_request(3, 'session/prompt', {
								sessionId: session_id,
								prompt: [{ type: 'text', text: `${task}\n\nIMPORTANT: Keep output concise with summary-first approach. Show key results only, no detailed breakdowns or verbose reasoning.` }]
							});
						} catch (e) {
							finish(new ACPError(`Failed to send prompt: ${e.message}`));
						}
						return;
					}

					if (data.method === 'session/update') {
						const update = data.params?.update;
						if (update?.sessionUpdate === 'agent_message_chunk') {
							const content = update?.content;
							if (content?.type === 'text') {
								let text = content?.text || '';
								text = text.replace(/<thinking>[\s\S]*?<\/thinking>/g, '');
								if (text.trim()) output_chunks.push(text);
							}
						}
					}

					if (data.result?.stopReason === 'end_turn') {
						finish(null, { output: output_chunks.join('') });
					}
				} catch (e) {
					if (this.verbose && line && !line.startsWith('{')) {
						console.error(`Skipped non-JSON: ${line.substring(0, 100)}`);
					}
				}
			});

			try {
				this.send_request(1, 'initialize', { protocolVersion: 1, capabilities: {}, clientInfo: { name: 'claude-code', version: '1.0' } });
			} catch (e) {
				finish(new ACPError(`Failed to initialize: ${e.message}`));
				return;
			}

			setTimeout(() => {
				if (done) return;
				try {
					this.send_request(2, 'session/new', { cwd, mcpServers: [] });
					session_timer = setTimeout(() => {
						if (!done) finish(new ACPError(`Session creation timeout after ${SESSION_TIMEOUT}ms`));
					}, SESSION_TIMEOUT);
				} catch (e) {
					finish(new ACPError(`Failed to create session: ${e.message}`));
				}
			}, 200);
		});
	}
}

async function main() {
	const args = process.argv.slice(2);
	if (args.length < 2 || args.includes('--help') || args.includes('-h')) {
		console.error('Usage: node acp_client.cjs <cwd> <task> -o <output_file> [-t timeout] [-v]');
		console.error('  -o FILE  Output file (required)');
		console.error('  -t SEC   Timeout in seconds (default: 1800)');
		console.error('  -v       Verbose mode');
		process.exit(1);
	}

	const cwd = args[0];
	const task = args[1];

	let output_file = null, timeout = 1800, verbose = false;
	for (let i = 0; i < args.length; i++) {
		if (args[i] === '-o' && args[i + 1]) { output_file = args[i + 1]; i++; }
		else if (args[i] === '-t' && args[i + 1]) { timeout = parseFloat(args[i + 1]) || 1800; i++; }
		else if (args[i] === '-v') verbose = true;
	}

	if (!output_file) {
		console.error('✗ Error: -o output file is required');
		process.exit(3);
	}

	const client = new ACPClient(verbose);
	try {
		const result = await client.execute_task(cwd, task, timeout);
		fs.writeFileSync(output_file, result.output);
		console.log('✓ Subagent task completed');
		process.exit(0);
	} catch (e) {
		if (e instanceof ACPTimeoutError) {
			console.error(`✗ Timeout: ${e.message}`);
			process.exit(2);
		} else if (e instanceof ACPError) {
			console.error(`✗ Error: ${e.message}`);
			process.exit(3);
		} else {
			console.error(`✗ Unexpected error: ${e.message}`);
			process.exit(4);
		}
	}
}

if (require.main === module) main();
module.exports = { ACPClient, ACPError, ACPTimeoutError };
