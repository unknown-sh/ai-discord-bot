// CLI test harness for llm_router.js
const { llmRouteCommand } = require('./llm_router');

(async () => {
  const input = process.argv.slice(2).join(' ');
  if (!input) {
    console.error('Usage: node llm_router_test.js "your natural language command"');
    process.exit(1);
  }
  try {
    const result = await llmRouteCommand(input);
    console.log('LLM Router Output:');
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(2);
  }
})();
