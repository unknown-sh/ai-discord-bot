import openai
import requests
import logging
from ai_gateway.supabase_config import get_config

# --- Provider Handlers ---

def ask_openai(prompt):
    messages = []

    personality = get_config("AI_PERSONALITY")
    if personality:
        messages.append({"role": "system", "content": personality})

    messages.append({"role": "user", "content": prompt})

    model = get_config("OPENAI_MODEL") or "gpt-4"
    temperature = float(get_config("OPENAI_TEMPERATURE") or "0.7")
    max_tokens = int(get_config("OPENAI_MAX_TOKENS") or "1000")
    top_p = float(get_config("OPENAI_TOP_P") or "1.0")
    presence_penalty = float(get_config("OPENAI_PRESENCE_PENALTY") or "0.0")
    frequency_penalty = float(get_config("OPENAI_FREQUENCY_PENALTY") or "0.0")
    api_key = get_config("OPENAI_API_KEY")

    if not api_key:
        logging.error("[OpenAI] Missing OPENAI_API_KEY")
        return "OpenAI API key is not configured."

    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty
        )
        return response.choices[0].message["content"]
    except Exception as e:
        logging.error(f"[OpenAI API Error] {e}")
        return "There was an error while processing your request with OpenAI."

async def ask_anthropic(prompt):
    personality = await get_config("AI_PERSONALITY")
    full_prompt = f"{personality}\n\nHuman: {prompt}\n\nAssistant:" if personality else prompt

    api_key = await get_config("ANTHROPIC_API_KEY")
    model = await get_config("ANTHROPIC_MODEL") or "claude-3-opus-20240229"
    temperature = float(await get_config("ANTHROPIC_TEMPERATURE") or "0.7")
    max_tokens = int(await get_config("ANTHROPIC_MAX_TOKENS") or "1000")

    if not api_key:
        logging.error("[Anthropic] Missing ANTHROPIC_API_KEY")
        return "Anthropic API key is not configured."

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "prompt": full_prompt
    }
    try:
        res = requests.post("https://api.anthropic.com/v1/complete", json=body, headers=headers, timeout=30)
        res.raise_for_status()
        return res.json()["completion"]
    except Exception as e:
        logging.error(f"[Anthropic API Error] {e} | Response: {getattr(res, 'text', 'No response')}")
        return "There was an error while processing your request with Anthropic."

async def ask_mistral(prompt):
    personality = await get_config("AI_PERSONALITY")
    full_prompt = f"{personality}\n\n{prompt}" if personality else prompt

    api_key = await get_config("MISTRAL_API_KEY")
    model = await get_config("MISTRAL_MODEL") or "mistral-medium"
    base_url = await get_config("MISTRAL_BASE_URL") or "https://api.mistral.ai"
    temperature = float(await get_config("MISTRAL_TEMPERATURE") or "0.7")
    max_tokens = int(await get_config("MISTRAL_MAX_TOKENS") or "1000")

    if not api_key:
        logging.error("[Mistral] Missing MISTRAL_API_KEY")
        return "Mistral API key is not configured."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        res = requests.post(f"{base_url}/v1/chat/completions", json=body, headers=headers, timeout=30)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"[Mistral API Error] {e} | Response: {getattr(res, 'text', 'No response')}")
        return "There was an error while processing your request with Mistral."

def ask(prompt):
    provider = get_config("AI_PROVIDER") or "openai"
    if provider == "openai":
        return ask_openai(prompt)
    elif provider == "anthropic":
        return ask_anthropic(prompt)
    elif provider == "mistral":
        return ask_mistral(prompt)
    else:
        raise ValueError(f"Unsupported AI_PROVIDER: {provider}")