// Help command handler
module.exports = async function handleHelpCommand(message, args, axios, logger) {
  // You can expand this to fetch help from the gateway or return static help
  const helpText = [
    '**Bot Commands:**',
    '',
    '**Config Commands:**',
    '`@bot config show` — Show current config (admin only)',
    '`@bot config show <key>` — Show a specific config key (admin only)',
    '`@bot config set <key> <value>` — Set config (admin only)',
    '`@bot config delete <key>` — Delete config (superadmin only)',
    '`@bot config list` or `@bot config keys` — List config keys (admin only)',
    '`@bot config help [<key>]` — Show config help or help for a specific key',
    '',
    '**Role Commands:**',
    '`@bot role show <@user>` — Show user role (admin only)',
    '`@bot role show all` — List all roles (admin only)',
    '`@bot role set <@user> <role>` — Set user role (superadmin only)',
    '',
    '**Audit Commands:**',
    '`@bot audit log [limit]` — Show recent audit log entries (superadmin only)',
    '',
    'Just @mention me with your question or prompt and I will reply with an AI-generated answer!'
  ].join('\n');
  await message.reply(helpText);
}
