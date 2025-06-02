// Role command handler
module.exports = async function handleRoleCommand(message, args, axios, logger, hasRole, getDiscordHeaders, formatErrorReply) {
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
  // Example: role show, role set, etc.
  if (args[0] === 'show') {
    // role show <@user> or role show all
    if (!hasRole(userRole, 'admin')) {
      await message.reply('\u26d4 You must be admin or above to view roles.');
      return;
    }
    if (args.length === 2 && args[1].toLowerCase() === 'all') {
      // List all roles and their users
      try {
        const res = await axios.get('http://ai-gateway:8000/acl/all', {
          headers: getDiscordHeaders(message)
        });
        if (Array.isArray(res.data) && res.data.length > 0) {
          const grouped = res.data.reduce((acc, row) => {
            if (!acc[row.role]) acc[row.role] = [];
            acc[row.role].push(`<@${row.user_id}>`);
            return acc;
          }, {});
          let reply = '**Roles:**\n';
          for (const [role, users] of Object.entries(grouped)) {
            reply += `- **${role}**: ${users.join(', ')}\n`;
          }
          await message.reply(reply);
        } else {
          await message.reply('No roles found.');
        }
      } catch (err) {
        logger.error(`Failed to fetch all roles: ${err.message}`);
        await message.reply(formatErrorReply(err, '\u274c Failed to fetch all roles.'));
      }
    } else if (args.length === 2) {
      if (!hasRole(userRole, 'admin')) {
        await message.reply('\u26d4 You must be admin or above to view roles.');
        return;
      }
      // role show <@user>
      const userMention = args[1];
      const match = userMention.match(/^<@!?([0-9]+)>$/);
      if (!match) {
        await message.reply('Usage: `@bot role show <@user>` or `@bot role show all`');
        return;
      }
      const userId = match[1];
      try {
        const res = await axios.get(`http://ai-gateway:8000/acl/role/${userId}`, {
          headers: getDiscordHeaders(message)
        });
        const role = res.data.role;
        await message.reply(`<@${userId}> has role: **${role}**`);
      } catch (err) {
        logger.error(`Failed to fetch user role: ${err.message}`);
        await message.reply(formatErrorReply(err, '\u274c Failed to fetch user role.'));
      }
    } else {
      await message.reply('Usage: `@bot role show <@user>` or `@bot role show all`');
    }
  } else if (args[0] === 'set' && args.length === 3) {
    // role set <@user> <role>
    if (!hasRole(userRole, 'superadmin')) {
      logger.info(`${message.author.username} (${message.author.id}) attempted role set without sufficient role: ${userRole}`);
      await message.reply('⛔ You must be superadmin to set roles.');
      return;
    }
    const userMention = args[1];
    const match = userMention.match(/^<@!?([0-9]+)>$/);
    if (!match) {
      await message.reply('Usage: `@bot role set <@user> <role>`');
      return;
    }
    const userId = match[1];
    const newRole = args[2].toLowerCase();
    try {
      const res = await axios.post('http://ai-gateway:8000/acl/set', {
        user_id: userId,
        role: newRole
      }, {
        headers: getDiscordHeaders(message)
      });
      await message.reply(`✅ Set <@${userId}>'s role to **${newRole}**`);
    } catch (err) {
      logger.error(`Failed to set user role: ${err.message}`);
      await message.reply(formatErrorReply(err, '❌ Failed to set user role.'));
    }
  } else {
    const usage = [
      '**Role Command Usage:**',
      '`@bot role show <@user>` — Show user role (admin only)',
      '`@bot role show all` — List all roles (admin only)',
      '`@bot role set <@user> <role>` — Set user role (superadmin only)',
    ].join('\n');
    await message.reply(usage);
  }
};
