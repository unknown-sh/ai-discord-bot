import os
import openai
import requests

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
AI_PERSONALITY = os.getenv("AI_PERSONALITY", "")

# --- OpenAI ---
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
openai_top_p = float(os.getenv("OPENAI_TOP_P", "1.0"))
openai_presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", "0.0"))
openai_frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", "0.0"))

# --- Anthropic ---
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
anthropic_temperature = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))
anthropic_max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "1000"))

# --- Mistral ---
mistral_api_key = os.getenv("MISTRAL_API_KEY")
mistral_model = os.getenv("MISTRAL_MODEL", "mistral-medium")
mistral_base_url = os.getenv("MISTRAL_BASE_URL", "https://api.mistral.ai")
mistral_temperature = float(os.getenv("MISTRAL_TEMPERATURE", "0.7"))
mistral_max_tokens = int(os.getenv("MISTRAL_MAX_TOKENS", "1000"))

# --- Provider Handlers ---

def ask_openai(prompt):
    messages = []

    if AI_PERSONALITY:
        messages.append({"role": "system", "content": AI_PERSONALITY})

    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=messages,
        temperature=openai_temperature,
        max_tokens=openai_max_tokens,
        top_p=openai_top_p,
        presence_penalty=openai_presence_penalty,
        frequency_penalty=openai_frequency_penalty
    )
    return response.choices[0].message["content"]

def ask_anthropic(prompt):
    full_prompt = f"{AI_PERSONALITY}\n\nHuman: {prompt}\n\nAssistant:" if AI_PERSONALITY else prompt

    headers = {
        "x-api-key": anthropic_api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": anthropic_model,
        "max_tokens": anthropic_max_tokens,
        "temperature": anthropic_temperature,
        "messages": [{"role": "user", "content": full_prompt}]
    }
    res = requests.post("https://api.anthropic.com/v1/messages", json=body, headers=headers)
    return res.json()["content"][0]["text"]

def ask_mistral(prompt):
    full_prompt = f"{AI_PERSONALITY}\n\n{prompt}" if AI_PERSONALITY else prompt

    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": mistral_model,
        "messages": [{"role": "user", "content": full_prompt}],
        "temperature": mistral_temperature,
        "max_tokens": mistral_max_tokens
    }
    res = requests.post(f"{mistral_base_url}/v1/chat/completions", json=body, headers=headers)
    return res.json()["choices"][0]["message"]["content"]

def ask(prompt):
    if AI_PROVIDER == "openai":
        return ask_openai(prompt)
    elif AI_PROVIDER == "anthropic":
        return ask_anthropic(prompt)
    elif AI_PROVIDER == "mistral":
        return ask_mistral(prompt)
    else:
        raise ValueError(f"Unsupported AI_PROVIDER: {AI_PROVIDER}")