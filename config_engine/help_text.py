COMMANDS = {
    "help": "Show this message, help for a specific command, or list all commands. Usage: `@bot help`, `@bot help command <command>`, or `@bot show commands`.",
    "config": "View or update configuration values (models, keys, personality, etc).",
    "role": "Show or change access roles (admin/superadmin only).",
    "ask": "Send a prompt to the AI and get a response.",
    "about": "Show information about this bot.",
    "show": "Show config keys, current values, or list all commands. Usage: `@bot show config`, `@bot show config <key>`, or `@bot show commands`.",
}

COMMAND_HELP = {
    "help": (
        "Show help for all commands or a specific command.\n"
        "- General: `@bot help`\n"
        "- Command: `@bot help command <command>`"
    ),
    "config": (
        "View or set configuration values.\n"
        "- Show all: `@bot config show`\n"
        "- Show key: `@bot config show <key>`\n"
        "- Set: `@bot config set <key> <value>`"
    ),
    "role": (
        "Show or change user roles.\n"
        "- Show user: `@bot role show <@user or user_id>`\n"
        "- Show all: `@bot role showall`\n"
        "- Set: `@bot role set <@user or user_id> <role>` (superadmin only)\n"
        "- Remove: `@bot role remove <@user or user_id>` (superadmin only)"
    ),
    "ask": "Ask a question: `@bot ask <your question>`.",
    "about": "Show information about the bot: `@bot about`.",
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
    """
    Retrieves help text for a specific command.

    Args:
    command (str): The name of the command to retrieve help for.

    Returns:
    str: The help text for the command, or a fallback message if not found.
    """
    return COMMAND_HELP.get(command, f"No help found for command: {command}")


def format_config_help(param: str) -> str:
    """
    Retrieves help text for a specific configuration parameter.

    Args:
    param (str): The name of the configuration parameter to retrieve help for.

    Returns:
    str: The help text for the parameter, or a fallback message if not found.
    """
    help_info = CONFIG_HELP.get(param)
    if help_info:
        return f"{param}: {help_info['desc']}\nUsage: {help_info['usage']}"
    return f"No help found for config: {param}"


def list_all_configs() -> str:
    """
    Retrieves a comma-separated list of all configuration keys.

    Returns:
    str: A comma-separated list of configuration keys.
    """
    return ", ".join(CONFIG_HELP.keys())
