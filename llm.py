import os
import time
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_groq_client: Optional[Groq] = None

def get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable is missing. Please set it in .env file."
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client

def call_llm(prompt: str, system: Optional[str] = None, model: str = "llama-3.3-70b-versatile", max_retries: int = 2) -> str:
    """
    Wrapper around Groq API with explicit retry logic.
    Retries up to max_retries times on network/rate-limit/API errors.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    client = get_groq_client()

    for attempt in range(1, max_retries + 2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            if attempt <= max_retries:
                time.sleep(1.5 * attempt)
            else:
                raise RuntimeError(f"Groq LLM call failed after {max_retries + 1} attempts: {str(e)}") from e

if __name__ == "__main__":
    print("Testing Groq LLM wrapper module import...")
