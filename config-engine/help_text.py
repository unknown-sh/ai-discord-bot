COMMANDS = {
    "help": "Show this message or help for a specific command.",
    "command": "Invoke a bot command (e.g., config set).",
    "config": "View or update configuration.",
    "role": "Show or change access roles (admin/superadmin only).",
}

COMMAND_HELP = {
    "config": (
        "Use `@bot config set <key> <value>` to change configuration (e.g., model, provider, personality).\n"
        "Use `@bot config show` to view all config settings.\n"
        "Use `@bot help config <key>` to get help for a specific setting."
    ),
    "role": (
        "Use `@bot role show <@user>` to check a user's role.\n"
        "Use `@bot role set <@user> <role>` to change it (superadmin-only).\n"
        "Use `@bot role list` to view all assigned roles."
    ),
}

CONFIG_HELP = {
    "personality": {
        "desc": "Controls the tone/persona of the bot.",
        "usage": "@bot config set personality <new-persona>",
    },
    "provider": {
        "desc": "Changes the AI backend (openai, anthropic, mistral).",
        "usage": "@bot config set provider openai",
    },
    "model": {
        "desc": "Changes the model for the current provider.",
        "usage": "@bot config set model gpt-4",
    },
    "temperature": {
        "desc": "Sets the creativity level for responses (0.0–1.0).",
        "usage": "@bot config set temperature 0.7",
    },
    "max_tokens": {
        "desc": "Limits the maximum length of a single response.",
        "usage": "@bot config set max_tokens 1000",
    },
    "top_p": {
        "desc": "Controls diversity via nucleus sampling (0.0–1.0).",
        "usage": "@bot config set top_p 1.0",
    },
    "presence_penalty": {
        "desc": "Penalizes repeating topics already mentioned (OpenAI only).",
        "usage": "@bot config set presence_penalty 0.0",
    },
    "frequency_penalty": {
        "desc": "Penalizes frequent word usage (OpenAI only).",
        "usage": "@bot config set frequency_penalty 0.0",
    },
    # Add more config options here as needed
    "log_file": {
        "desc": "Sets the file name where bot commands and config changes are logged.",
        "usage": "@bot config set log_file bot_actions.log",
    },
    "ai_provider": {
        "desc": "Overrides the AI provider globally (openai, anthropic, mistral).",
        "usage": "@bot config set ai_provider openai",
    },
    "openai_api_key": {
        "desc": "OpenAI API key used for model calls. Restricted to secure use.",
        "usage": "@bot config set openai_api_key sk-***",
    },
    "anthropic_api_key": {
        "desc": "Anthropic API key used for model calls. Restricted to secure use.",
        "usage": "@bot config set anthropic_api_key your-anthropic-api-key",
    },
    "anthropic_model": {
        "desc": "Changes the Anthropic model (e.g., claude-3-opus-20240229).",
        "usage": "@bot config set anthropic_model claude-3-opus-20240229",
    },
    "anthropic_temperature": {
        "desc": "Sets response creativity for Anthropic models.",
        "usage": "@bot config set anthropic_temperature 0.7",
    },
    "anthropic_max_tokens": {
        "desc": "Limits max tokens returned by Anthropic models.",
        "usage": "@bot config set anthropic_max_tokens 1000",
    },
    "mistral_api_key": {
        "desc": "Mistral API key used for model calls. Restricted to secure use.",
        "usage": "@bot config set mistral_api_key your-mistral-api-key",
    },
    "mistral_model": {
        "desc": "Changes the Mistral model (e.g., mistral-medium).",
        "usage": "@bot config set mistral_model mistral-medium",
    },
    "mistral_base_url": {
        "desc": "Base URL for Mistral API (if using self-hosted endpoint).",
        "usage": "@bot config set mistral_base_url https://api.mistral.ai",
    },
    "mistral_temperature": {
        "desc": "Sets response creativity for Mistral models.",
        "usage": "@bot config set mistral_temperature 0.7",
    },
    "mistral_max_tokens": {
        "desc": "Limits max tokens returned by Mistral models.",
        "usage": "@bot config set mistral_max_tokens 1000",
    },
}
