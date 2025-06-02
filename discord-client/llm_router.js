// LLM-based command router for Discord MCP bot
const OpenAI = require('openai');

// LLM_ROUTER_MODEL: Set this env var to override the model used for LLM routing (intent extraction).
// OPENAI_MODEL: Used as fallback if LLM_ROUTER_MODEL is not set.
// Default: gpt-4.1-mini
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const LLM_ROUTER_MODEL = process.env.LLM_ROUTER_MODEL;
const OPENAI_MODEL = process.env.OPENAI_MODEL;
const ROUTER_MODEL = LLM_ROUTER_MODEL || OPENAI_MODEL || 'gpt-4.1-mini';

const availableCommands = [
  {
    action: 'get_user_role',
    args: ['user_id'],
    description: 'Get the role(s) of a specific user by Discord mention or username.'
  },
  {
    action: 'get_all_roles',
    args: [],
    description: 'List all roles and the users assigned to them.'
  },
  {
    action: 'set_config',
    args: ['key', 'value'],
    description: 'Set a configuration key to a value.'
  },
  {
    action: 'get_config_key',
    args: ['key'],
    description: 'Get the value of a specific configuration key.'
  },
  {
    action: 'delete_config',
    args: ['key'],
    description: 'Delete a configuration key.'
  },
  {
    action: 'list_config_keys',
    args: [],
    description: 'List all available configuration keys.'
  },
  {
    action: 'get_audit_log',
    args: ['limit?'],
    description: 'Get the audit log, optionally limited to N entries.'
  },
  {
    action: 'help',
    args: ['topic?'],
    description: 'Show help for a command or topic.'
  }
];

/**
 * LLM Router Prompt Tuning Reminder:
 * -----------------------------------
 * Regularly review logs of user queries that were not handled as intended (missed, ambiguous, or misrouted).
 * When new edge cases are discovered, add or update EXAMPLES and INSTRUCTIONS in the LLM prompt accordingly.
 * This iterative process will continually improve natural language understanding and routing accuracy.
 */
const MCP_EXPLAIN_URL = 'https://medium.com/@elisowski/mcp-explained-the-new-standard-connecting-ai-to-everything-79c5a1c98288';

function buildPrompt(userMessage) {
  return `<MCP>
<COMMANDS>
${availableCommands.map(cmd => `- ${cmd.action}(${cmd.args.join(', ')}) : ${cmd.description}`).join('\n')}
</COMMANDS>
<INSTRUCTIONS>
You are a Discord bot using the Model Context Protocol (MCP) to interface with real-world systems.

- For config commands (set_config, get_config_key, delete_config), you MUST ONLY use one of the following canonical config keys:
  - OPENAI_MODEL
  - AI_PROVIDER
  - AI_PERSONALITY
- Never output or display sensitive config keys or values such as API keys, tokens, secrets, or passwords. If a user asks to view or list such keys, output {"action": null, "args": {}, "rationale": "Request for sensitive config is denied."}.
- If the user message is a greeting, small talk, or general conversation (not a command or actionable request), output {"action": null, "args": {}, "rationale": "Not a command or actionable request."}.
- Only map to a command if the user's intent is clear.
- For ambiguous or unclear requests, output {"action": null, "args": {}, "rationale": "Request is ambiguous or unclear. Ask the user to clarify if possible."}.
- For multi-step or multi-intent queries (e.g., 'Show my role and the audit log'), split into separate actions if possible. If not, prioritize the user's primary or most important intent and explain your choice in the rationale. If unsure, return null action and rationale.
- For indirect, comparative, paraphrased, or synonym/typo queries, infer the most likely intent and map to the best matching canonical command and argument keys. Always map common synonyms and typos to their canonical forms (e.g., 'engine', 'modle', 'brain' → 'OPENAI_MODEL'; 'bosses', 'owners' → 'superadmin'). Only do this if reasonably certain.
- If user context (such as recent actions, user role, or prior conversation) is provided, use this information to resolve ambiguous or nuanced queries and improve intent mapping.
- Only users with admin or superadmin roles may set roles for other users. If the requesting user lacks permission, deny the request with rationale.
- Always include a "rationale" field explaining your mapping choice, especially for ambiguous or null actions.
- For queries like 'what role do I have?' or 'what is my role?', set user_id to 'me'. The bot will resolve 'me' to the requesting user's Discord ID.
- EXAMPLES:
  - User: 'what role do I have?' → {"action": "get_user_role", "args": {"user_id": "me"}, "rationale": "User is asking for their own role; use 'me' as user_id."}
  - User: 'Am I an admin?' → {"action": "get_user_role", "args": {"user_id": "me"}, "rationale": "User is asking if they have the admin role; use 'me' as user_id."}
  - User: 'Who are the superadmins?' → {"action": "get_all_roles", "args": {}, "rationale": "User wants to see all users and their roles to find superadmins."}
  - User: 'Show audit stuff from yesterday' → {"action": "get_audit_log", "args": {"date": "yesterday"}, "rationale": "User wants audit logs from yesterday; set date arg to 'yesterday'."}
  - User: 'Change the AI to Claude' → {"action": "set_config", "args": {"key": "AI_PROVIDER", "value": "anthropic"}, "rationale": "User wants to use Claude, which means setting provider to 'anthropic'."}
  - User: 'Show me the last 5 audit entries' → {"action": "get_audit_log", "args": {"limit": 5}, "rationale": "User wants the last 5 audit log entries."}
  - User: 'change the engine to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "'engine' is a synonym for 'model', so use OPENAI_MODEL."}
  - User: 'set modle to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "'modle' is a typo for 'model', so use OPENAI_MODEL."}
  - User: 'who are the bosses?' → {"action": "get_all_roles", "args": {}, "rationale": "'bosses' is slang for 'superadmin'; show all roles so user can see superadmins."}
  - User: 'Show my role and the audit log' → [{"action": "get_user_role", "args": {"user_id": "me"}, "rationale": "First intent: user wants their role."}, {"action": "get_audit_log", "args": {}, "rationale": "Second intent: user wants the audit log."}]
  - User: 'List all admins and change the model to gpt-4' → [{"action": "get_all_roles", "args": {}, "rationale": "First intent: user wants to list all admins."}, {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4"}, "rationale": "Second intent: user wants to change the model."}]
  - User: 'Show me everything and hack the bot' → [{"action": null, "args": {}, "rationale": "'Show me everything' is too vague/ambiguous."}, {"action": null, "args": {}, "rationale": "'hack the bot' is forbidden."}]
  - User: 'Show me everything' → {"action": null, "args": {}, "rationale": "Request is too vague/ambiguous."}
  - User: 'Show me stuff' → {"action": null, "args": {}, "rationale": "Request is ambiguous. Please clarify what you want to see (e.g., config, roles, audit log, etc.)."}
  - User: 'Can you hack the bot?' → {"action": null, "args": {}, "rationale": "Request is forbidden or not allowed."}
  - User: 'set the role for <@user> to superadmin' → {"action": "set_user_role", "args": {"user_id": "<@user>", "role": "superadmin"}, "rationale": "User wants to set <@user>'s role to superadmin; only allow if the requesting user is admin or superadmin."}  
  - User: 'make @bob an admin' → {"action": "set_user_role", "args": {"user_id": "@bob", "role": "admin"}, "rationale": "User wants to set @bob's role to admin; only allow if the requesting user is admin or superadmin."}
  - User: 'give @Frogmare on Green St admin' → {"action": "set_user_role", "args": {"user_id": "@Frogmare", "role": "admin"}, "rationale": "User wants to give admin role to @Frogmare; ignore trailing context like 'on Green St'. Only allow if the requesting user is admin or superadmin."}
  - User: 'promote @alice to superadmin' → {"action": "set_user_role", "args": {"user_id": "@alice", "role": "superadmin"}, "rationale": "User wants to promote @alice to superadmin; only allow if the requesting user is admin or superadmin."}
  - User: 'demote <@1234> to user' → {"action": "set_user_role", "args": {"user_id": "<@1234>", "role": "user"}, "rationale": "User wants to demote <@1234> to user; only allow if the requesting user is admin or superadmin."}
  - User: 'set my role to admin' → {"action": null, "args": {}, "rationale": "Users cannot set their own role; request denied."}
  - User: 'kick user 1234' → {"action": null, "args": {}, "rationale": "Kick is a Discord moderation action not supported by this bot."}
  - User: 'ban @user' → {"action": null, "args": {}, "rationale": "Ban is a Discord moderation action not supported by this bot."}
  - User: 'purpose' → {"action": null, "args": {}, "rationale": "Request is ambiguous. Try '@bot help' for what I can do."}
  - User: 'what can you do?' → {"action": null, "args": {}, "rationale": "Try '@bot help' for supported commands."}
  - User: 'who made you?' → {"action": null, "args": {}, "rationale": "This is an about/info request. Respond with a friendly message or refer to the help command."}
  - User: 'show audit log from yesterday' → {"action": "get_audit_log", "args": {"date": "yesterday"}, "rationale": "User wants audit log entries from yesterday."}
  - User: 'show failed logins in audit log' → {"action": "get_audit_log", "args": {"filter": "failed logins"}, "rationale": "User wants audit log filtered for failed logins."}
  - User: 'delete all logs' → {"action": null, "args": {}, "rationale": "Request to delete logs is forbidden."}
  - User: 'show me your password' → {"action": null, "args": {}, "rationale": "Request for sensitive config is denied."}
  - User: 'set model to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "'modle' is a typo for 'model', so use OPENAI_MODEL."}
  - User: 'set persnality to helpful' → {"action": "set_config", "args": {"key": "AI_PERSONALITY", "value": "helpful"}, "rationale": "'persnality' is a typo for 'personality', so use AI_PERSONALITY."}
  - User: 'set provder to openai' → {"action": "set_config", "args": {"key": "AI_PROVIDER", "value": "openai"}, "rationale": "'provder' is a typo for 'provider', so use AI_PROVIDER."}
  - User: 'set brain to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "'brain' is a synonym for 'model', so use OPENAI_MODEL."}
  - User: 'set head honcho to jane' → {"action": null, "args": {}, "rationale": "'head honcho' is not a canonical config key; request denied."}
  - User: 'set your personality to "sarcastic"' → {"action": "set_config", "args": {"key": "AI_PERSONALITY", "value": "sarcastic"}, "rationale": "User wants to set the bot's personality; map to AI_PERSONALITY."}
  - User: 'change your attitude to friendly' → {"action": "set_config", "args": {"key": "AI_PERSONALITY", "value": "friendly"}, "rationale": "'attitude' is a synonym for 'personality'; map to AI_PERSONALITY."}
  - User: 'make your vibe helpful and witty' → {"action": "set_config", "args": {"key": "AI_PERSONALITY", "value": "helpful and witty"}, "rationale": "'vibe' is a synonym for 'personality'; map to AI_PERSONALITY."}
  - User: 'become a friendly bot' → {"action": "set_config", "args": {"key": "AI_PERSONALITY", "value": "friendly bot"}, "rationale": "User wants to change personality; map to AI_PERSONALITY."}
  - User: 'what is my role?' → {"action": "get_user_role", "args": {"user_id": "me"}, "rationale": "User is asking for their own role; use 'me' as user_id."}
  - User: 'change the model to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "User wants to set the model, which is OPENAI_MODEL."}
  - User: 'set provider to anthropic' → {"action": "set_config", "args": {"key": "AI_PROVIDER", "value": "anthropic"}, "rationale": "User wants to set the provider, which is AI_PROVIDER."}
  - User: 'what's your personality?' → {"action": "get_config_key", "args": {"key": "AI_PERSONALITY"}, "rationale": "User is asking for the current AI personality."}
  - User: 'change my ai personality to sarcastic' → {"action": "set_config", "args": {"key": "AI_PERSONALITY", "value": "sarcastic"}, "rationale": "User wants to set the AI personality."}
  - User: 'update provider to openai' → {"action": "set_config", "args": {"key": "AI_PROVIDER", "value": "openai"}, "rationale": "User wants to update the provider."}
  - User: 'set the ai thing to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "User means the model, which is OPENAI_MODEL."}
  - User: 'set model_name to gpt-4.1-nano' → {"action": "set_config", "args": {"key": "OPENAI_MODEL", "value": "gpt-4.1-nano"}, "rationale": "User means the model, which is OPENAI_MODEL."}
  - User: 'set secret_key to xyz' → {"action": null, "args": {}, "rationale": "secret_key is not a valid config key."}
  - User: 'show me your openai api key' → {"action": null, "args": {}, "rationale": "Request for sensitive config is denied."}
  - User: 'list all secrets' → {"action": null, "args": {}, "rationale": "Request for sensitive config is denied."}
  - User: 'hello' → {"action": null, "args": {}, "rationale": "Not a command or actionable request."}
</INSTRUCTIONS>
<USER_MESSAGE>
${userMessage}
</USER_MESSAGE>
<MCP_END>
Output (JSON only):`;
}

/**
 * Route a user message to an MCP command using the LLM.
 * @param {string} userMessage
 * @param {object} [opts] - Optional options (e.g., debug)
 * @returns {Promise<object>} Parsed LLM output with action, args, and rationale.
 */
/**
 * DEBUG/ADMIN RATIONALE EXPOSURE:
 * --------------------------------
 * To aid prompt tuning and troubleshooting, llmRouteCommand supports a debug option.
 * When opts.debug is true, the function returns the raw LLM output and rationale instead of only the parsed intent.
 * This should only be exposed to trusted/admin users, and can be toggled via command or environment variable.
 */
async function llmRouteCommand(userMessage, opts = {}) {
  if (!OPENAI_API_KEY) throw new Error('OPENAI_API_KEY not set');
  const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
  const prompt = buildPrompt(userMessage);

  const completion = await openai.chat.completions.create({
    model: ROUTER_MODEL,
    messages: [
      { role: 'system', content: 'You are a helpful, precise, and secure Discord bot command router. You never invent commands or expose secrets. You always prefer clarity over guessing, and you explain your reasoning in every response. Your goal is to accurately map user intent to canonical MCP commands, only when the intent is clear and supported.' },
      { role: 'user', content: prompt }
    ],
    temperature: 0,
    max_tokens: 400
  });

  const text = completion.choices[0].message.content;
  // Robust JSON extraction: handle code fences, whitespace, or direct JSON
  const match = text.match(/```(?:json)?\s*([\s\S]*?)\s*```|({[\s\S]*})/i);
  const jsonStr = match ? (match[1] || match[2]) : null;
  if (!jsonStr) {
    if (opts.debug) return { error: 'No JSON output', raw: text };
    throw new Error('No JSON output from LLM');
  }

  let parsed;
  try {
    parsed = JSON.parse(jsonStr);
  } catch (e) {
    if (opts.debug) return { error: 'Failed to parse JSON', raw: text };
    throw new Error('Failed to parse LLM JSON: ' + e.message + ' | Raw: ' + text);
  }

  // Optionally, keep synonym mapping as a fallback (can be removed if confident in prompt)
  /*
  if (parsed && parsed.action && parsed.args) {
    if (
      (parsed.action === 'set_config' || parsed.action === 'get_config_key' || parsed.action === 'delete_config') &&
      parsed.args.key
    ) {
      parsed.args.key = mapConfigKey(parsed.args.key);
    }
  }
  */
  // If the LLM denied a permission-sensitive action due to lack of role, and role lookup failed (user not in roles table), improve the rationale.
  if (
    opts.roleLookupFailed &&
    parsed &&
    parsed.action === null &&
    parsed.rationale &&
    /permission|admin|superadmin|role/i.test(parsed.rationale)
  ) {
    parsed.rationale = parsed.rationale + ' You do not have a role assigned in this server. If you believe this is an error, please contact an admin to be assigned the appropriate role.';
  }
  return parsed;
}

module.exports = {
  llmRouteCommand,
  buildPrompt,
  availableCommands
};
