"""
Lightweight LLM client wrapper.

Works with ANY OpenAI-compatible API:
  - Groq            (free, fast)  -> https://console.groq.com  (recommended for students)
  - OpenAI          -> https://platform.openai.com
  - Together / Fireworks / Ollama (local) / etc.

Set LLM_API_KEY, LLM_BASE_URL and optionally LLM_MODEL (see .env.example).
"""

import os
from openai import OpenAI


def get_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY is not set. Copy .env.example to .env and add your key.\n"
            "Free key: https://console.groq.com/keys"
        )
    return OpenAI(api_key=api_key, base_url=base_url)


def chat(messages, temperature: float = 0.0) -> str:
    client = get_client()
    model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
