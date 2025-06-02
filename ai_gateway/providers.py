import logging
from typing import Optional

import aiohttp
import openai
from ai_gateway.supabase_config import get_config


def mask_api_key(key: Optional[str]) -> str:
    """
    Mask an API key for logging purposes.
    """
    if not key or len(key) < 8:
        return "****"
    return f"{key[:8]}...{'*' * (len(key) - 12)}"


# --- Provider Handlers ---


async def ask_openai(prompt: str) -> str:
    """
    Ask OpenAI's chat model asynchronously with error handling and logging.
    Returns the generated response as a string.
    """
    messages = []
    personality = await get_config("AI_PERSONALITY")
    if personality:
        messages.append({"role": "system", "content": personality})
    messages.append({"role": "user", "content": prompt})

    model = await get_config("OPENAI_MODEL") or "gpt-4"
    temperature = float(await get_config("OPENAI_TEMPERATURE") or "0.7")
    max_tokens = int(await get_config("OPENAI_MAX_TOKENS") or "1000")
    top_p = float(await get_config("OPENAI_TOP_P") or "1.0")
    presence_penalty = float(await get_config("OPENAI_PRESENCE_PENALTY") or "0.0")
    frequency_penalty = float(await get_config("OPENAI_FREQUENCY_PENALTY") or "0.0")
    api_key = await get_config("OPENAI_API_KEY")

    if not api_key:
        logging.error("[OpenAI] Missing OPENAI_API_KEY")
        return "OpenAI API key is not configured."

    client = openai.AsyncOpenAI(api_key=api_key)

    try:
        logging.info(
            f"[OpenAI] Sending prompt: {prompt!r} | Model: {model} | Key: {mask_api_key(api_key)}"
        )
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        result = response.choices[0].message.content
        if not result or not str(result).strip():
            logging.warning(
                f"[OpenAI] Empty response for prompt: {prompt!r} | Raw: {response}"
            )
            return "Sorry, I couldn't generate a response."
        return result
    except Exception as e:
        import traceback
        # Try to extract response body from OpenAI error if available
        error_message = str(e)
        error_body = None
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            try:
                error_body = await e.response.text()
            except Exception:
                error_body = None
        logging.error(
            f"[OpenAI API Error] {error_message}\nPrompt: {prompt!r}\nModel: {model}\nKey: {mask_api_key(api_key)}\nTraceback: {traceback.format_exc()}\nOpenAI Response: {error_body}"
        )
        # Return detailed error to user for debugging
        return f"OpenAI API error: {error_message}\n{error_body if error_body else ''}"


async def ask_anthropic(prompt: str) -> str:
    """
    Ask Anthropic's Claude model asynchronously with error handling and logging.
    Returns the generated response as a string.
    """
    personality = await get_config("AI_PERSONALITY")
    full_prompt = (
        f"{personality}\n\nHuman: {prompt}\n\nAssistant:" if personality else prompt
    )

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
        "anthropic-version": "2023-06-01",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "prompt": full_prompt,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/complete",
                json=body,
                headers=headers,
                timeout=30,
            ) as res:
                res.raise_for_status()
                data = await res.json()
                return data["completion"]
    except Exception as e:
        logging.error(f"[Anthropic API Error] {e}")
        return "There was an error while processing your request with Anthropic."


async def ask_mistral(prompt: str) -> str:
    """
    Ask Mistral's chat model asynchronously with error handling and logging.
    Returns the generated response as a string.
    """
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

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/v1/chat/completions",
                json=body,
                headers=headers,
                timeout=30,
            ) as res:
                res.raise_for_status()
                data = await res.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"[Mistral API Error] {e}")
        return "There was an error while processing your request with Mistral."


async def ask(prompt: str) -> str:
    """
    Route prompt to the configured AI provider asynchronously.
    Returns the generated response as a string.
    """
    provider = await get_config("AI_PROVIDER") or "openai"
    if provider == "openai":
        return await ask_openai(prompt)
    elif provider == "anthropic":
        return await ask_anthropic(prompt)
    elif provider == "mistral":
        return await ask_mistral(prompt)
    else:
        raise ValueError(f"Unsupported AI_PROVIDER: {provider}")
