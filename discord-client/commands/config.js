// Config command handler
module.exports = async function handleConfigCommand(message, args, axios, logger, hasRole, getDiscordHeaders, formatErrorReply) {
  // Always check Supabase role for permissions
  let userRole = 'guest';
  try {
    const res = await axios.get(`http://ai-gateway:8000/acl/role/${message.author.id}`, {
      headers: getDiscordHeaders(message)
    });
    userRole = res.data.role || 'guest';
  } catch (err) {
    logger.warn(`Could not fetch Supabase role for ${message.author.id}: ${err.message}`);
  }
  if (args[0] === 'show') {
    if (!hasRole(userRole, 'admin')) {
      return message.reply(`\u26d4 You must be admin or above to view config.`);
    }
    logger.info(`${message.author.username} (${message.author.id}): ${message.content}`);
    try {
      if (args.length === 1) {
        const headers = getDiscordHeaders(message);
        if (!headers['X-User-ID']) {
          logger.error('Config show failed: Missing user ID in headers');
          return message.reply('❌ Internal error: Missing user ID for access control.');
        }
        const res = await axios.get('http://ai-gateway:8000/config/status', {
          headers
        });
        const { provider, model, personality } = res.data;
        return message.reply(`\ud83d\udee0\ufe0f **Current Config:**\n- Provider: \`${provider}\`\n- Model: \`${model}\`\n- Personality: \`${personality || '(not set)'}\``);
      } else if (args.length === 2) {
        const headers = getDiscordHeaders(message);
        if (!headers['X-User-ID']) {
          logger.error('Config show failed: Missing user ID in headers');
          return message.reply('❌ Internal error: Missing user ID for access control.');
        }
        const key = args[1];
        const res = await axios.get(`http://ai-gateway:8000/show/config/${key}`, {
          headers
        });
        return message.reply(res.data.text);
      } else {
      return message.reply('\u2753 Usage: `@bot config show` or `@bot config show <key>`');
      }
    } catch (err) {
      logger.error(`Config show failed: ${err.message}`);
      return message.reply(formatErrorReply(err, `\u274c Failed to retrieve config.`));
    }
  }
  // --- CONFIG SET COMMAND (multi-word value support) ---
  if (args[0] === 'set') {
    if (!hasRole(userRole, 'admin')) {
      logger.info(`${message.author.username} (${message.author.id}) attempted config set without sufficient role: ${userRole}`);
      return message.reply(`\u26d4 You must be admin or above to set config.`);
    }
    if (args.length < 3) {
      return message.reply('\u2753 Usage: `@bot config set <key> <value>`');
    }
    const key = args[1];
    const value = args.slice(2).join(' ');
    const headers = getDiscordHeaders(message);
    if (!headers['X-User-ID']) {
      logger.error('Config set failed: Missing user ID in headers');
      return message.reply('❌ Internal error: Missing user ID for access control.');
    }
    logger.info(`${message.author.username} (${message.author.id}) [${userRole}]: config set ${key} = ${value}`);
    try {
      const res = await axios.post(`http://ai-gateway:8000/set/config/${key}`, { value }, { headers });
      if (res.data && res.data.status === 'ok') {
        return message.reply(`✅ Config \`${key}\` set to \`${value}\`.`);
      } else {
        logger.error(`Config set failed for ${key}: unexpected response ${JSON.stringify(res.data)}`);
        return message.reply(formatErrorReply(res, `❌ Failed to set config.`));
      }
    } catch (err) {
      logger.error(`Config set failed for ${key}: ${err.message}`);
      return message.reply(formatErrorReply(err, `❌ Failed to set config.`));
    }
  }

  // --- CONFIG DELETE COMMAND (superadmin only) ---
  if (args[0] === 'delete') {
    if (!hasRole(userRole, 'superadmin')) {
      logger.info(`${message.author.username} (${message.author.id}) attempted config delete without sufficient role: ${userRole}`);
      return message.reply('⛔ You must be superadmin to delete config keys.');
    }
    if (args.length !== 2) {
      return message.reply('🗑️ Usage: `@bot config delete <key>`');
    }
    const key = args[1];
    const headers = getDiscordHeaders(message);
    logger.info(`${message.author.username} (${message.author.id}) [${userRole}]: config delete ${key}`);
    try {
      const res = await axios.delete(`http://ai-gateway:8000/delete/config/${key}`, { headers });
      if (res.data && res.data.status && res.data.status.startsWith('deleted')) {
        return message.reply(`🗑️ Config key \`${key}\` deleted.`);
      } else {
        logger.error(`Config delete failed for ${key}: unexpected response ${JSON.stringify(res.data)}`);
        return message.reply(formatErrorReply(res, `❌ Failed to delete config.`));
      }
    } catch (err) {
      logger.error(`Config delete failed for ${key}: ${err.message}`);
      return message.reply(formatErrorReply(err, `❌ Failed to delete config.`));
    }
  }

  // --- CONFIG LIST/KEYS COMMAND ---
  if (args[0] === 'list' || args[0] === 'keys') {
    if (!hasRole(userRole, 'admin')) {
      return message.reply('⛔ You must be admin or above to list config keys.');
    }
    const headers = getDiscordHeaders(message);
    try {
      const res = await axios.get('http://ai-gateway:8000/show/config', { headers });
      if (res.data && res.data.text) {
        return message.reply(res.data.text);
      } else {
        logger.error(`Config list/keys failed: unexpected response ${JSON.stringify(res.data)}`);
        return message.reply('❌ Failed to list config keys.');
      }
    } catch (err) {
      logger.error(`Config list/keys failed: ${err.message}`);
      return message.reply(formatErrorReply(err, `❌ Failed to list config keys.`));
    }
  }

  // --- CONFIG HELP COMMAND ---
  if (args[0] === 'help') {
    const headers = getDiscordHeaders(message);
    if (args.length === 2) {
      // Help for a specific config key
      try {
        const key = args[1];
        const res = await axios.get(`http://ai-gateway:8000/help/config/${key}`, { headers });
        if (res.data && res.data.text) {
          return message.reply(res.data.text);
        } else {
          return message.reply('❓ No help available for that config key.');
        }
      } catch (err) {
        logger.error(`Config help failed: ${err.message}`);
        return message.reply(formatErrorReply(err, `❌ Failed to fetch config help.`));
      }
    } else {
      // General config help
      try {
        const res = await axios.get('http://ai-gateway:8000/help/config', { headers });
        if (res.data && res.data.text) {
          return message.reply(res.data.text);
        } else {
          return message.reply('❓ No config help available.');
        }
      } catch (err) {
        logger.error(`Config help failed: ${err.message}`);
        return message.reply(formatErrorReply(err, `❌ Failed to fetch config help.`));
      }
    }
  }

  // --- UNKNOWN/INVALID SUBCOMMANDS ---
  const usage = [
    '**Config Command Usage:**',
    '`@bot config show` — Show current config (admin only)',
    '`@bot config show <key>` — Show a specific config key (admin only)',
    '`@bot config set <key> <value>` — Set config (admin only)',
    '`@bot config delete <key>` — Delete config (superadmin only)',
    '`@bot config list` or `@bot config keys` — List config keys (admin only)',
    '`@bot config help [<key>]` — Show config help or help for a specific key',
  ].join('\n');
  return message.reply(usage);

};
