// Main Discord bot entry point (modularized)
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');
const path = require('path');
const { createLogger, format, transports } = require('winston');
require('winston-daily-rotate-file');

const config = require('./bot-config');
const hasRole = require('./utils/hasRole');
const getDiscordHeaders = require('./utils/getDiscordHeaders');
const formatErrorReply = require('./utils/formatErrorReply');

// Ensure logs directory exists before logger setup
const fs = require('fs');
const logsDir = path.join(__dirname, 'logs');
try {
  fs.mkdirSync(logsDir, { recursive: true });
} catch (e) {
  // If directory can't be created, fallback to console logging only
  console.warn('[startup] Could not create logs directory:', logsDir, e);
}

// Logger setup
const logFormat = format.printf(({ timestamp, level, message }) => {
  return `[${timestamp}] ${level.toUpperCase()}: ${message}`;
});
const logger = createLogger({
  level: 'info',
  format: format.combine(format.timestamp(), logFormat),
  transports: [
    new transports.DailyRotateFile({
      filename: path.join(__dirname, 'bot_actions-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: process.env.LOG_MAX_BYTES || '5m',
      maxFiles: process.env.LOG_BACKUP_COUNT || '3d',
      zippedArchive: true
    }),
    new transports.Console()
  ]
});

function assertEnvVars(vars) {
  for (const v of vars) {
    if (!process.env[v]) {
      logger.error(`Missing required environment variable: ${v}`);
      throw new Error(`Missing required environment variable: ${v}`);
    }
  }
}
assertEnvVars(['DISCORD_TOKEN']);

// Import command handlers
const handleHelpCommand = require('./commands/help');
const handleConfigCommand = require('./commands/config');
const handleRoleCommand = require('./commands/role');
const handleAskCommand = require('./commands/ask');
const handleAuditCommand = require('./commands/audit');

// Start HTTP healthcheck server (for Docker)
require('./healthz');

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

client.on('ready', () => {
  logger.info(`Logged in as ${client.user.tag}`);
});

const tryHandleNaturalLanguageMcp = require('./mcp_nl_handler');

client.on('messageCreate', async (message) => {
  logger.info(`[MSG EVENT] Received message: ${message.content} from ${message.author.tag}`);
  if (message.author.bot) return;

  // Only respond if the bot is mentioned (by @mention or direct message)
  const botWasMentioned = message.mentions.has(client.user);
  const isDirectMessage = message.channel.type === 1 || message.channel.type === 'dm';
  if (!botWasMentioned && !isDirectMessage) return;

  // Remove the mention from the message content if present
  let input = message.content.trim();
  if (botWasMentioned) {
    const mention = `<@${client.user.id}>`;
    if (input.startsWith(mention)) {
      input = input.slice(mention.length).trim();
    }
  }
  const args = input.split(/\s+/).filter(Boolean);
  const commandRaw = args.shift();
  const command = commandRaw ? commandRaw.toLowerCase() : '';

  try {
    if (command === 'help') {
      await handleHelpCommand(message, args, axios, logger);
    } else if (command === 'config') {
      await handleConfigCommand(message, args, axios, logger, hasRole, getDiscordHeaders, formatErrorReply);
    } else if (command === 'role') {
      await handleRoleCommand(message, args, axios, logger, hasRole, getDiscordHeaders, formatErrorReply);
    } else if (command === 'audit') {
      await handleAuditCommand(message, args, axios, logger, hasRole, getDiscordHeaders, formatErrorReply);
    } else {
      // Try natural language MCP handler as fallback
      const handled = await tryHandleNaturalLanguageMcp(message, logger);
      if (!handled) {
        // Any other message: treat as AI prompt (including one-word messages like 'hello')
        const aiArgs = [command, ...args].filter(Boolean);
        await handleAskCommand(message, aiArgs, axios, logger, getDiscordHeaders, formatErrorReply);
      }
    }
  } catch (err) {
    logger.error(`Command error: ${err.message}`);
    await message.reply(formatErrorReply(err, '❌ Bot error.'));
  }
});

client.login(config.discordToken);
