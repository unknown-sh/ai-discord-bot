// Audit command handler
module.exports = async function handleAuditCommand(message, args, axios, logger, hasRole, getDiscordHeaders, formatErrorReply) {
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

  // audit log [limit]
  if (args[0] === 'log') {
    if (!hasRole(userRole, 'superadmin')) {
      logger.info(`${message.author.username} (${message.author.id}) attempted audit log without sufficient role: ${userRole}`);
      return message.reply('⛔ You must be superadmin to view audit logs.');
    }
    let limit = 10;
    if (args.length === 2 && !isNaN(parseInt(args[1]))) {
      limit = Math.max(1, Math.min(100, parseInt(args[1])));
    }
    const headers = getDiscordHeaders(message);
    logger.info(`${message.author.username} (${message.author.id}) [${userRole}]: audit log (limit=${limit})`);
    try {
      const limit = args[1] && !isNaN(args[1]) ? Number(args[1]) : 10;
      let res;
      try {
        res = await axios.get(`http://ai-gateway:8000/mcp/audit/logs?limit=${limit}`, { headers });
      } catch (err) {
        if (err.response && err.response.status === 404) {
          return message.reply('No audit logs found.');
        }
        throw err;
      }
      if (res.data && Array.isArray(res.data.logs)) {
        if (res.data.logs.length === 0) {
          return message.reply('No audit log entries found.');
        }
        let reply = '**Recent Audit Log Entries:**\n';
        for (const entry of res.data.logs) {
          reply += `- [${entry.timestamp}] ${entry.username || entry.user_id}: ${entry.action}`;
          if (entry.ip) reply += ` (IP: ${entry.ip})`;
          reply += '\n';
        }
        return message.reply(reply.slice(0, 1800)); // Discord message limit
      } else {
        logger.error(`Audit log fetch failed: unexpected response ${JSON.stringify(res.data)}`);
        return message.reply('❌ Failed to fetch audit log.');
      }
    } catch (err) {
      logger.error(`Audit log fetch failed: ${err.message}`);
      return message.reply(formatErrorReply(err, `❌ Failed to fetch audit log.`));
    }
  }

  // Unknown/invalid subcommands
  const usage = [
    '**Audit Command Usage:**',
    '`@bot audit log [limit]` — Show recent audit log entries (superadmin only)',
  ].join('\n');
  return message.reply(usage);
};
