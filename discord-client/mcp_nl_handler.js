// Advanced Natural Language to MCP Action Handler for Discord Bot
const nlp = require('compromise');
const axios = require('axios');
const { llmRouteCommand } = require('./llm_router');
const getDiscordHeaders = require('./utils/getDiscordHeaders');
const formatErrorReply = require('./utils/formatErrorReply');
const MCP_BASE_URL = process.env.MCP_SERVER_URL || process.env.MCP_BASE_URL || 'http://localhost:8000';

// --- ADVANCED INTENT TEMPLATES (expandable) ---
const intentTemplates = [
  {
    action: 'get_all_roles',
    patterns: [
      'what roles are available',
      'list all roles',
      'show me all roles',
      'show me the roles',
      'show roles',
      'roles',
      'display all roles',
      'who can do what',
      'show all permissions'
    ]
  },
  {
    action: 'get_user_role',
    patterns: [
      'what role does [user]',
      'show role for [user]',
      'who is [user]',
      'what permissions does [user] have',
      'show me [user] role',
      'what can [user] do',
    ],
    extractEntities: (doc, message) => {
      // Try to extract a mention or numeric ID from anywhere
      let match = message.match(/<@!?([0-9]+)>/);
      if (match) {
        return { user_id: match[1] };
      }
      // Try to extract a plain numeric ID
      match = message.match(/role (?:does|of|for|is) ([0-9]{6,}) have|role for ([0-9]{6,})/i);
      if (match) {
        const id = match[1] || match[2];
        if (id) return { user_id: id.trim() };
      }
      // Try to extract username (fuzzy)
      match = message.match(/role (?:does|of|for|is) ([\w\s]+) have|role for ([\w\s]+)/i);
      if (match) {
        const name = match[1] || match[2];
        if (name) return { user_id: name.trim() };
      }
      // Fallback to NLP tags
      const user = doc.match('#Mention').text();
      if (user) return { user_id: user.replace(/[<@!>]/g, '') };
      const person = doc.match('#Person').text();
      if (person) return { user_id: person };
      return null;
    }
  },
  {
    action: 'set_user_role',
    patterns: [
      'set [user] role to [role]',
      'make [user] an [role]',
      'promote [user] to [role]',
      'demote [user] to [role]',
      'change [user] to [role]'
    ],
    extractEntities: (doc, message) => {
      // Try to extract "set @user role to admin", "make @user an admin", etc.
      // 1. Try Discord mention with role
      let match = message.match(/<@!?([0-9]+)>.*\b(admin|superadmin|guest)\b/i);
      if (match) {
        return { user_id: match[1], role: match[2].toLowerCase() };
      }
      // 2. Try alternate phrasing: "make @user a role", "promote @user to role"
      match = message.match(/<@!?([0-9]+)>.*(?:to|as|an|a)\s+(admin|superadmin|guest)\b/i);
      if (match) {
        return { user_id: match[1], role: match[2].toLowerCase() };
      }
      // 3. Try @username with optional trailing context (e.g., 'on Green St')
      match = message.match(/@([\w\s]+?)(?:\s+on\s+.+)?\s+(admin|superadmin|guest)\b/i);
      if (match) {
        return { user_id: match[1].trim(), role: match[2].toLowerCase() };
      }
      // 4. Try just @username + role (no context)
      match = message.match(/@([\w\s]+)\s+(admin|superadmin|guest)\b/i);
      if (match) {
        return { user_id: match[1].trim(), role: match[2].toLowerCase() };
      }
      // 5. Fallback to NLP tags
      const user = doc.match('#Mention').text();
      const role = doc.match('(admin|superadmin|guest)').text();
      if (user && role) {
        return { user_id: user.replace(/[<@!>]/g, '').trim(), role: role.toLowerCase() };
      }
      // 6. Try fuzzy username extraction (first @ or first capitalized word before role)
      match = message.match(/([A-Z][a-zA-Z0-9_\s]+)\s+(admin|superadmin|guest)\b/i);
      if (match) {
        return { user_id: match[1].trim(), role: match[2].toLowerCase() };
      }
      // 7. Extraction failed: return null to trigger a helpful fallback message
      return null;
    }
  },
  {
    action: 'get_config',
    patterns: [
      'what is your current config',
      'show config',
      'display config',
      'list config',
      'show me the config',
    ]
  },
  {
    action: 'get_config_key',
    patterns: [
      'show config key [key]',
      'display value for [key]',
      'what is [key] config',
      'show me [key] config',
    ],
    extractEntities: (doc) => {
      const key = doc.match('#Noun+').text();
      return key ? { key: key.toUpperCase() } : null;
    }
  },
  {
    action: 'set_config',
    patterns: [
      'set config [key] to [value]',
      'change [key] to [value]',
      'update [key] config to [value]',
      'set [key] config [value]',
    ],
    extractEntities: async (doc, message, mcpConfigKeys) => {
      // Try to extract "set [the] <key> config to <value>" or similar
      let match = message.match(/(?:set|change|update) (?:the )?([\w\s\-]+?) config (?:to|=) (.+)/i);
      let key = match ? match[1].trim().toUpperCase() : null;
      let value = match ? match[2].trim() : null;
      // Fallback to NLP tags
      if (!key || !value) {
        key = doc.match('#Noun+').text();
        value = doc.match('#Value+').text();
        if (key) key = key.toUpperCase();
      }
      // Map natural language keys to canonical keys
      const staticMap = {
        'MODEL CONFIG': 'OPENAI_MODEL',
        'MODEL': 'OPENAI_MODEL',
        'AI PROVIDER': 'AI_PROVIDER',
        'PROVIDER': 'AI_PROVIDER',
        'PERSONALITY': 'AI_PERSONALITY',
        'TEMPERATURE': 'OPENAI_TEMPERATURE',
      };
      let canonicalKey = staticMap[key] || key;
      // Fuzzy match against MCP config keys if available
      if (mcpConfigKeys && Array.isArray(mcpConfigKeys)) {
        const best = mcpConfigKeys.find(k => k.toUpperCase() === canonicalKey) ||
          mcpConfigKeys.find(k => k.toUpperCase().includes(canonicalKey)) ||
          mcpConfigKeys.find(k => canonicalKey.includes(k.toUpperCase()));
        if (best) canonicalKey = best.toUpperCase();
      }
      return key && value ? { key: canonicalKey, value } : null;
    }
  },
  {
    action: 'delete_config',
    patterns: [
      'delete config [key]',
      'remove config [key]',
      'delete [key] config',
    ],
    extractEntities: (doc) => {
      const key = doc.match('#Noun+').text();
      return key ? { key: key.toUpperCase() } : null;
    }
  },
  {
    action: 'list_config_keys',
    patterns: [
      'list config keys',
      'show config keys',
      'display all config keys',
      'what config keys exist',
    ]
  },
  {
    action: 'get_audit_log',
    patterns: [
      'show me the last [number] lines of audit log',
      'audit log last [number]',
      'show audit log [number]',
      'display last [number] audit entries',
      'audit log recent [number]'
    ],
    extractEntities: (doc, message) => {
      // Try to extract a number from the original message (e.g., 'audit log 20')
      let match = message.match(/(?:audit|log|entries|last|recent|show)\s*(\d{1,3})/i);
      if (match) {
        return { limit: Math.max(1, Math.min(100, parseInt(match[1], 10))) };
      }
      // Fallback to NLP tags
      const num = doc.match('#Value').numbers().toNumber();
      return num ? { limit: num } : { limit: 10 };
    }
  },
  // Add more advanced patterns/intents here
];

function fuzzyKeywordMatch(message, action) {
  const msg = message.toLowerCase();
  // Roles (all roles)
  if (action === 'get_all_roles') {
    return /\broles?\b/.test(msg) && !/\bfor\b|\bof\b|\bdoes\b|\bwho\b|\buser\b/.test(msg);
  }
  // Roles (user role)
  if (action === 'get_user_role') {
    return /\broles?\b/.test(msg) && (/@\w+/.test(msg) || /\bfor\b|\bof\b|\bdoes\b|\bwho\b|\buser\b/.test(msg));
  }
  // Config (show all config)
  if (action === 'get_config') {
    return /\bconfig(uration)?\b/.test(msg) && /show|display|list|what|current/.test(msg);
  }
  // Config (show specific key)
  if (action === 'get_config_key') {
    return /\bconfig(uration)?\b/.test(msg) && /key|value|of|for|show/.test(msg);
  }
  // Config (set key)
  if (action === 'set_config') {
    return /\bset|change|update/.test(msg) && /config(uration)?\b/.test(msg);
  }
  // Config (delete key)
  if (action === 'delete_config') {
    return /\bdelete|remove/.test(msg) && /config(uration)?\b/.test(msg);
  }
  // Config (list keys)
  if (action === 'list_config_keys') {
    return /\bconfig(uration)?\b/.test(msg) && /keys/.test(msg);
  }
  // Audit log
  if (action === 'get_audit_log') {
    return /\baudit\b/.test(msg) && /log|entries|recent|last|show|display/.test(msg);
  }
  return false;
}

async function matchIntent(message, originalMessage, mcpConfigKeys) {
  const doc = nlp(message);
  for (const template of intentTemplates) {
    for (const pattern of template.patterns) {
      let testPattern = pattern
        .replace('[user]', '#Mention|#Person')
        .replace('[role]', '(admin|superadmin|guest|member|mod|moderator)')
        .replace('[key]', '#Noun+')
        .replace('[value]', '#Value+|#Adjective|#Noun+')
        .replace('[number]', '#Value');
      if (doc.has(testPattern)) {
        let params = template.extractEntities
          ? (template.action === 'set_config'
              ? await template.extractEntities(doc, originalMessage || message, mcpConfigKeys)
              : template.extractEntities(doc, originalMessage || message))
          : {};
        if (template.action === 'set_user_role' && !params.user_id) {
          const user = doc.match('#Person').text();
          const role = doc.match('(admin|superadmin|guest|member|mod|moderator)').text();
          if (user && role) params = { user_id: user, role };
        }
        if (template.action === 'set_config' && (!params.key || !params.value)) {
          const match = (originalMessage || message).match(/set (\w+) to ([^\s]+)/i);
          if (match) params = { key: match[1].toUpperCase(), value: match[2] };
        }
        return { action: template.action, params };
      }
    }
    if (fuzzyKeywordMatch(message, template.action)) {
      return { action: template.action, params: {} };
    }
  }
  return null;
}


// Monitoring/metrics counters (for future integration)
// let intentMatchCount = 0, openaiFallbackCount = 0, intentFailureCount = 0;


async function tryHandleNaturalLanguageMcp(message, logger) {
  const content = message.content.replace(/^<@!?\d+>\s*/, '').trim();
  let intent = null;
  let llmError = null;

  // 1. Try LLM-based routing first
  try {
    // Fetch user role for permission-sensitive actions
    let userRole = null;
    let roleLookupFailed = false;
    try {
      const res = await axios.get(`${MCP_BASE_URL}/acl/role/${message.author.id}`, { headers: getDiscordHeaders(message) });
      userRole = res.data.role || null;
    } catch (err) {
      if (err.response && err.response.status === 404) {
        userRole = 'guest';
        roleLookupFailed = true;
        logger.warn(`User ${message.author.id} not found in roles table; treating as guest.`);
      } else {
        logger.warn(`Could not fetch Supabase role for ${message.author.id}: ${err.message}`);
      }
    }
    intent = await llmRouteCommand(content, { userRole, roleLookupFailed });
    logger.info(`[LLM Router] action=${intent.action} args=${JSON.stringify(intent.args)} rationale=${intent.rationale || ''}`);
  } catch (err) {
    llmError = err;
    logger.warn(`LLM routing failed: ${err.message}`);
  }

  // 2. Fallback to NLP if LLM fails or gives no valid action
  if (!intent || !intent.action) {
    // (existing NLP fallback logic)
    let mcpConfigKeys = null;
    const isConfigSet = /set|change|update/.test(content) && /config(uration)?/i.test(content);
    if (isConfigSet) {
      try {
        const res = await axios.get(`${MCP_BASE_URL}/config/keys`, { headers: getDiscordHeaders(message) });
        if (res.data && Array.isArray(res.data.keys)) {
          mcpConfigKeys = res.data.keys.map(k => k.toUpperCase());
        }
      } catch (err) {
        logger.warn('Could not fetch MCP config keys for fuzzy mapping: ' + err.message);
      }
    }
    intent = await matchIntent(content, message.content, mcpConfigKeys);
    if (!intent) return false;
  }

  // Route to explicit command handlers for known commands
  const command = intent.action;
  const args = Object.values(intent.args || intent.params || {});
  if (command === 'get_user_role') {
    // If no user extracted, try to extract mention or numeric ID from message content
    let userIdArg = args[0];
    if (userIdArg === 'me') userIdArg = message.author.id;
    if (!userIdArg) {
      const mentionMatch = message.content.match(/<@!?([0-9]+)>/);
      if (mentionMatch) userIdArg = mentionMatch[1];
      else {
        const idMatch = message.content.match(/\b([0-9]{6,})\b/);
        if (idMatch) userIdArg = idMatch[1];
      }
    }
    if (userIdArg) {
      const handleRoleCommand = require('./commands/role');
      await handleRoleCommand(message, ['show', userIdArg], require('axios'), logger, require('./utils/hasRole'), require('./utils/getDiscordHeaders'), require('./utils/formatErrorReply'));
      return true;
    }
  }
  if (command === 'get_all_roles') {
    const handleRoleCommand = require('./commands/role');
    await handleRoleCommand(message, ['show', 'all'], require('axios'), logger, require('./utils/hasRole'), require('./utils/getDiscordHeaders'), require('./utils/formatErrorReply'));
    return true;
  }
  if (command === 'set_user_role') {
    const handleRoleCommand = require('./commands/role');
    await handleRoleCommand(message, ['set', ...args], require('axios'), logger, require('./utils/hasRole'), require('./utils/getDiscordHeaders'), require('./utils/formatErrorReply'));
    return true;
  }
  if (command === 'get_config' || command === 'get_config_key' || command === 'set_config' || command === 'delete_config' || command === 'list_config_keys') {
    const handleConfigCommand = require('./commands/config');
    let cmdArgs = ['show'];
    if (command === 'get_config_key' && args.length) cmdArgs = ['show', ...args];
    if (command === 'set_config' && args.length >= 2) cmdArgs = ['set', ...args];
    if (command === 'delete_config' && args.length) cmdArgs = ['delete', ...args];
    if (command === 'list_config_keys') cmdArgs = ['keys'];
    await handleConfigCommand(message, cmdArgs, require('axios'), logger, require('./utils/hasRole'), require('./utils/getDiscordHeaders'), require('./utils/formatErrorReply'));
    return true;
  }
  if (command === 'get_audit_log') {
    const handleAuditCommand = require('./commands/audit');
    let cmdArgs = ['log'];
    if (args.length && args[0]) cmdArgs.push(args[0]);
    await handleAuditCommand(message, cmdArgs, require('axios'), logger, require('./utils/hasRole'), require('./utils/getDiscordHeaders'), require('./utils/formatErrorReply'));
    return true;
  }
  if (command === 'help') {
    const handleHelpCommand = require('./commands/help');
    await handleHelpCommand(message, args, require('axios'), logger);
    return true;
  }

  return await callMcpAndReply(message, logger, command, intent.args || intent.params);
}



async function callMcpAndReply(message, logger, action, params) {
  logger.info(`[MCP Fallback] action=${action} params=${JSON.stringify(params)}`);
  const userId = message.author.id;
  try {
    let url = `${MCP_BASE_URL}/mcp/${action}`;
    let headers = getDiscordHeaders(message);
    headers['X-User-ID'] = userId;
    let response;
    // Special-case: if action requires a path param, inject it
    if (action === 'get_user_role' && params && params.user_id) {
      let userId = params.user_id;
      // If mention, extract numeric ID
      const mentionMatch = typeof userId === 'string' && userId.match(/^<@!?([0-9]+)>$/);
      if (mentionMatch) userId = mentionMatch[1];
      url = `${MCP_BASE_URL}/mcp/get_user_role/${encodeURIComponent(userId)}`;
      response = await axios.get(url, { headers });
    } else if (action === 'get_config_key' && params && params.key) {
      url = `${MCP_BASE_URL}/mcp/get_config_key/${encodeURIComponent(params.key)}`;
      response = await axios.get(url, { headers });
    } else if (action === 'set_config' && params && params.key) {
      url = `${MCP_BASE_URL}/mcp/set_config/${encodeURIComponent(params.key)}`;
      response = await axios.post(url, { value: params.value }, { headers });
    } else if (action.startsWith('get_') || action === 'list_config_keys') {
      const searchParams = new URLSearchParams(params).toString();
      response = await axios.get(url + (searchParams ? `?${searchParams}` : ''), { headers });
    } else if (action.startsWith('set_') || action.startsWith('delete_')) {
      if (action.startsWith('set_')) {
        response = await axios.post(url, params, { headers });
      } else {
        response = await axios.delete(url, { headers, data: params });
      }
    } else {
      response = await axios.post(url, params, { headers });
    }
    logger.info(`[MCP] Action ${action} params=${JSON.stringify(params)} result=${JSON.stringify(response.data)}`);
    await message.reply(formatMcpResult(action, response.data));
    return true;
  } catch (err) {
    // Improved error logging for debugging
    let errorDetails = err && err.toJSON ? JSON.stringify(err.toJSON()) : '';
    if (err && err.response) {
      errorDetails += ` | response status: ${err.response.status}, data: ${JSON.stringify(err.response.data)}`;
    }
    if (err && err.stack) {
      errorDetails += ` | stack: ${err.stack}`;
    }
    logger.error(`[MCP] Action ${action} failed: ${err.message} ${errorDetails}`);
    await message.reply(formatErrorReply(err, `\u274c MCP action failed: ${err.message} ${errorDetails}`));
    return true;
  }
}

// OpenAI fallback for fuzzy intent suggestion
async function openaiIntentSuggest(content, logger) {
  try {
    const configuration = new Configuration({ apiKey: process.env.OPENAI_API_KEY });
    const openai = new OpenAIApi(configuration);
    // Prepare the available actions and a prompt
    const actions = intentTemplates.map(t => t.action).join(', ');
    const prompt = `Given the following bot actions: ${actions}. For the message: '${content}', return the best action and parameters as JSON, e.g. { "action": "get_user_role", "params": { "user_id": "123" } }.`;
    const completion = await openai.createChatCompletion({
      model: process.env.OPENAI_MODEL || 'gpt-3.5-turbo',
      messages: [
        { role: 'system', content: 'You are an intent extraction assistant for a Discord bot.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 100,
      temperature: 0
    });
    const text = completion.data.choices[0].message.content.trim();
    logger.info(`[OpenAI] Intent suggestion raw: ${text}`);
    // Try to parse JSON from response
    const match = text.match(/\{[\s\S]*\}/);
    if (match) {
      return JSON.parse(match[0]);
    }
    return null;
  } catch (err) {
    logger.warn(`[OpenAI] Intent suggestion failed: ${err.message}`);
    return null;
  }
}

function formatMcpResult(action, data) {
  // Simple formatting per action (expand as needed)
  switch (action) {
    case 'get_all_roles':
      if (Array.isArray(data)) {
        // Group users by role and mention by user_id
        const grouped = data.reduce((acc, row) => {
          if (!acc[row.role]) acc[row.role] = [];
          acc[row.role].push(`<@${row.user_id}>`);
          return acc;
        }, {});
        let reply = '**Roles:**\n';
        for (const [role, users] of Object.entries(grouped)) {
          reply += `- **${role}**: ${users.join(', ')}\n`;
        }
        return reply.trim();
      } else if (data && data.roles) {
        // Object format (legacy)
        return '**Roles:**\n' + Object.entries(data.roles).map(([role, users]) => `- **${role}**: ${users.join(', ')}`).join('\n');
      } else if (typeof data === 'object' && data !== null) {
        // Fallback: print object keys
        return '**Roles:**\n' + Object.entries(data).map(([k,v]) => `- ${k}: ${JSON.stringify(v)}`).join('\n');
      }
      break;
    case 'get_user_role':
      if (data && data.username && data.role) {
        return `**${data.username}** has role: **${data.role}**`;
      } else if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([k,v]) => `- ${k}: ${v}`).join('\n');
      }
      break;
    case 'get_config':
      if (data && typeof data === 'object') {
        return '**Config:**\n' + Object.entries(data).map(([k, v]) => `- ${k}: ${v}`).join('\n');
      } else if (typeof data !== 'undefined') {
        return `Config: ${JSON.stringify(data)}`;
      }
      break;
    case 'get_config_key':
      if (data && data.key && typeof data.value !== 'undefined') {
        return `Config **${data.key}**: ${data.value}`;
      } else if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([k,v]) => `- ${k}: ${v}`).join('\n');
      }
      break;
    case 'set_config':
      if (data && data.key && typeof data.value !== 'undefined') {
        return `Set config **${data.key}** to: ${data.value}`;
      } else if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([k,v]) => `- ${k}: ${v}`).join('\n');
      }
      break;
    case 'delete_config':
      if (data && data.key) {
        return `Deleted config **${data.key}**`;
      } else if (typeof data === 'object' && data !== null) {
        return Object.entries(data).map(([k,v]) => `- ${k}: ${v}`).join('\n');
      }
      break;
    case 'list_config_keys':
      if (data && Array.isArray(data.keys)) {
        return '**Config Keys:**\n' + data.keys.join(', ');
      } else if (Array.isArray(data)) {
        return '**Config Keys:**\n' + data.join(', ');
      }
      break;
    case 'get_audit_log':
      if (data && Array.isArray(data.logs)) {
        return '**Audit Log:**\n' + data.logs.map(e => `- [${e.timestamp}] ${e.username || e.user_id}: ${e.action}`).join('\n');
      } else if (Array.isArray(data)) {
        return '**Audit Log:**\n' + data.map(e => `- [${e.timestamp}] ${e.username || e.user_id}: ${e.action}`).join('\n');
      }
      break;
    default:
      // Fallback: pretty-print object or array, otherwise JSON
      if (typeof data === 'object' && data !== null) {
        if (Array.isArray(data)) {
          return data.map(e => JSON.stringify(e)).join('\n');
        }
        return Object.entries(data).map(([k,v]) => `- ${k}: ${JSON.stringify(v)}`).join('\n');
      }
      return typeof data !== 'undefined' ? String(data) : '✅ Action completed.';
  }
  return '✅ Action completed.';
}

module.exports = tryHandleNaturalLanguageMcp;
