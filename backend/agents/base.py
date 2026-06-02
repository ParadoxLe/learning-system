from openai import OpenAI, AsyncOpenAI
from backend.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME


class BaseAgent:
    """Base Agent — all specialized agents inherit from this.

    Encapsulates DeepSeek API calls. Subclasses set their own system_prompt
    and call self.chat() or self.chat_stream().
    """

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
        self.async_client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )

    def chat(self, user_message: str, temperature: float = 0.7) -> str:
        """Send a message to DeepSeek and return the text response."""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def chat_stream(self, user_message: str, temperature: float = 0.7):
        """Stream tokens from DeepSeek. Yields content deltas."""
        stream = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    def chat_with_history(self, history: list[dict], temperature: float = 0.7) -> str:
        """Send a full conversation history (including system prompt)."""
        messages = [{"role": "system", "content": self.system_prompt}] + history
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""

    def chat_with_history_stream(self, history: list[dict], temperature: float = 0.7):
        """Stream tokens from a full conversation history."""
        messages = [{"role": "system", "content": self.system_prompt}] + history
        stream = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    async def chat_with_history_stream_async(self, history: list[dict], temperature: float = 0.7):
        """Async stream tokens from a full conversation history."""
        messages = [{"role": "system", "content": self.system_prompt}] + history
        stream = await self.async_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
