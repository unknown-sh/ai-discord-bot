COMMANDS = {
    "help": "Show this message or help for a specific command.",
    "config": "View or update configuration values (models, keys, personality, etc).",
    "role": "Show or change access roles (admin/superadmin only).",
    "ask": "Send a prompt to the AI and get a response.",
    "about": "Show information about this bot.",
}

COMMAND_HELP = {
    "help": "Show this message or help for a specific command. Usage: `@bot help [command]`.",
    "config": (
        "Change or view configuration.\n"
        "- Set: `@bot config set <key> <value>`\n"
        "- Show all: `@bot config show`\n"
        "- Get help: `@bot help config <key>`\n"
        "- Example: `@bot config set model gpt-4`"
    ),
    "role": (
        "Show or change roles.\n"
        "- Show: `@bot role show <@user>`\n"
        "- Set: `@bot role set <@user> <role>` (superadmin only)\n"
        "- List: `@bot role list`"
    ),
    "ask": "Send a prompt to the AI and get a response. Usage: `@bot ask <your question>`.",
    "about": "Show information about this bot. Usage: `@bot about`.",
}

CONFIG_HELP = {
    # Personality and model
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
    # API keys (masked in logs, not shown in help)
    "openai_api_key": {
        "desc": "OpenAI API key used for model calls. Restricted to secure use.",
        "usage": "@bot config set openai_api_key sk-***",
    },
    "anthropic_api_key": {
        "desc": "Anthropic API key used for model calls. Restricted to secure use.",
        "usage": "@bot config set anthropic_api_key your-anthropic-api-key",
    },
    "mistral_api_key": {
        "desc": "Mistral API key used for model calls. Restricted to secure use.",
        "usage": "@bot config set mistral_api_key your-mistral-api-key",
    },
    # Anthropic
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
    # Mistral
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
    # Logging
    "log_file": {
        "desc": "Sets the file name where bot commands and config changes are logged.",
        "usage": "@bot config set log_file bot_actions.log",
    },
}

def format_command_help(command: str) -> str:
    if command in COMMAND_HELP:
        return COMMAND_HELP[command]
    elif command in COMMANDS:
        return f"{command}: {COMMANDS[command]}"
    else:
        return "No help found for this command."

def format_config_help(param: str) -> str:
    info = CONFIG_HELP.get(param)
    if info:
        return f"**{param}**: {info['desc']}\nUsage: `{info['usage']}`"
    else:
        return f"No help found for config: {param}"

def list_all_configs() -> str:
    return ", ".join(sorted(CONFIG_HELP.keys()))
