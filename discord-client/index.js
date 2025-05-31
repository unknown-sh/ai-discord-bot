const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');
const config = require('./bot-config');

const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

client.on('ready', () => {
  console.log(`Bot is logged in as ${client.user.tag}`);
});

client.on('messageCreate', async message => {
  if (message.author.bot) return;
  if (!message.mentions.has(client.user)) return;

  const input = message.content.replace(/<@!?(\d+)>/, '').trim();
  const [command, ...args] = input.split(/\s+/);

  if (command === 'help') {
    if (args[0] === 'command' && args[1]) {
      const res = await axios.get(`http://ai-gateway:8000/help/command/${args[1]}`);
      return message.reply(res.data.text);
    } else if (args[0] === 'config' && args[1]) {
      const res = await axios.get(`http://ai-gateway:8000/help/config/${args[1]}`);
      return message.reply(res.data.text);
    } else {
      const res = await axios.get(`http://ai-gateway:8000/help`);
      return message.reply(res.data.text);
    }
  }

  if (command === 'config' && args[0] === 'set' && args.length >= 3) {
    const key = args[1];
    const value = args.slice(2).join(' ');
    await axios.post(`http://ai-gateway:8000/config/${key}`, { value });
    return message.reply(`✅ Config updated: **${key} = ${value}**`);
  }

  // Default: treat as prompt
  const response = await axios.post('http://ai-gateway:8000/ask', { message: input });
  await message.reply(response.data.reply);
});

client.login(config.discordToken);