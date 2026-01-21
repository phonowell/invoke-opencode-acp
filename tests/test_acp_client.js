/** Unit tests for acp_client.cjs */
const { ACPClient, ACPError, ACPTimeoutError } = require('../skills/invoke-opencode-acp/acp_client.cjs');
const assert = require('assert');

// Test helper
function test(name, fn) {
	try {
		fn();
		console.log(`✓ ${name}`);
	} catch (e) {
		console.error(`✗ ${name}: ${e.message}`);
		process.exit(1);
	}
}

console.log('\n=== Running acp_client.cjs tests ===\n');

// ===== Error Classes =====
test('ACPError extends Error', () => {
	const err = new ACPError('test error');
	assert.strictEqual(err.name, 'ACPError');
	assert.strictEqual(err.message, 'test error');
	assert.ok(err instanceof Error);
});

test('ACPTimeoutError extends ACPError', () => {
	const err = new ACPTimeoutError('timeout');
	assert.strictEqual(err.name, 'ACPTimeoutError');
	assert.ok(err instanceof ACPError);
	assert.ok(err instanceof Error);
});

test('ACPTimeoutError can be caught as ACPError', () => {
	let caught = false;
	try {
		throw new ACPTimeoutError('timeout');
	} catch (e) {
		if (e instanceof ACPError) {
			caught = true;
			assert.ok(e.message.includes('timeout'));
		}
	}
	assert.ok(caught);
});

// ===== ACPClient Constructor =====
test('ACPClient init with verbose', () => {
	const client = new ACPClient(true);
	assert.strictEqual(client.verbose, true);
	assert.strictEqual(client.proc, null);
});

test('ACPClient init default', () => {
	const client = new ACPClient();
	assert.strictEqual(client.verbose, false);
	assert.strictEqual(client.proc, null);
});

// ===== send_request =====
test('send_request throws when process not started', () => {
	const client = new ACPClient();
	assert.throws(() => {
		client.send_request(1, 'test', {});
	}, /Process not started/);
});

// ===== Thinking Filter =====
test('Thinking filter removes single block', () => {
	const text = '<thinking>reasoning</thinking>result';
	const filtered = text.replace(/<thinking>[\s\S]*?<\/thinking>/g, '');
	assert.strictEqual(filtered, 'result');
});

test('Thinking filter removes multiline block', () => {
	const text = 'before<thinking>\nmultiline\nreasoning\n</thinking>after';
	const filtered = text.replace(/<thinking>[\s\S]*?<\/thinking>/g, '');
	assert.strictEqual(filtered, 'beforeafter');
});

test('Thinking filter removes multiple blocks', () => {
	const text = 'a<thinking>1</thinking>b<thinking>2</thinking>c';
	const filtered = text.replace(/<thinking>[\s\S]*?<\/thinking>/g, '');
	assert.strictEqual(filtered, 'abc');
});

test('Thinking filter handles empty block', () => {
	const text = 'start<thinking></thinking>end';
	const filtered = text.replace(/<thinking>[\s\S]*?<\/thinking>/g, '');
	assert.strictEqual(filtered, 'startend');
});

test('Thinking filter preserves text without blocks', () => {
	const text = 'just normal text';
	const filtered = text.replace(/<thinking>[\s\S]*?<\/thinking>/g, '');
	assert.strictEqual(filtered, 'just normal text');
});

// ===== execute_task (integration - mocked) =====
// Note: Full integration tests would require mocking subprocess.spawn
// These are unit-level validations only

console.log('\n=== All tests passed ===\n');
