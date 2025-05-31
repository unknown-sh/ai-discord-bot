module.exports = {
  discordToken: process.env.DISCORD_TOKEN || "",
  botName: process.env.BOT_NAME || "Brax",
  commandPrefix: process.env.COMMAND_PREFIX || "@mention",
  environment: process.env.NODE_ENV || "development",

  // Supabase
  supabaseUrl: process.env.SUPABASE_URL || "",
  supabaseKey: process.env.SUPABASE_KEY || "",

  // AI Defaults
  defaultModel: process.env.OPENAI_MODEL || "gpt-4.1-nano",
  defaultProvider: process.env.AI_PROVIDER || "openai",

  // Optional logging level toggle
  debug: process.env.DEBUG === "true"
};