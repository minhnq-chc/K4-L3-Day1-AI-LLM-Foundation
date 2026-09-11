import os
import time
from typing import Any, Callable

from dotenv import load_dotenv

load_dotenv()

PRICING_PER_1K_TOKENS = {
    "gpt-4o": {"input": 0.0025, "output": 0.010},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}

OPENAI_MODEL = os.getenv("LAB_MODEL", "gpt-4o")
OPENAI_MINI_MODEL = os.getenv("LAB_MINI_MODEL", "gpt-4o-mini")


def call_openai(prompt: str, model: str = OPENAI_MODEL, temperature: float = 0.7,
                top_p: float = 0.9, max_tokens: int = 256) -> tuple[str, float]:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}],
        temperature=temperature, top_p=top_p, max_tokens=max_tokens,
    )
    return response.choices[0].message.content, time.perf_counter() - start


def call_openai_mini(prompt: str, temperature: float = 0.7, top_p: float = 0.9,
                     max_tokens: int = 256) -> tuple[str, float]:
    return call_openai(prompt, model=OPENAI_MINI_MODEL, temperature=temperature,
                       top_p=top_p, max_tokens=max_tokens)


def compare_models(prompt: str) -> dict:
    large_text, large_latency = call_openai(prompt)
    mini_text, mini_latency = call_openai_mini(prompt)
    cost = (len(large_text.split()) / 0.75) / 1000 * PRICING_PER_1K_TOKENS["gpt-4o"]["output"]
    return {"gpt4o_response": large_text, "mini_response": mini_text,
            "gpt4o_latency": large_latency, "mini_latency": mini_latency,
            "gpt4o_cost_estimate": cost}


def chat_with_system_prompt(system_prompt: str, user_prompt: str,
                            model: str = OPENAI_MODEL, temperature: float = 0.7,
                            max_tokens: int = 256) -> tuple[str, float]:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        temperature=temperature, max_tokens=max_tokens,
    )
    return response.choices[0].message.content, time.perf_counter() - start


def count_tokens(text: str, model: str = OPENAI_MODEL) -> int:
    try:
        import tiktoken
        return len(tiktoken.encoding_for_model(model).encode(text))
    except Exception:
        return max(1, len(text) // 4)


def estimate_cost(prompt: str, response: str, model: str = OPENAI_MODEL) -> dict:
    input_tokens, output_tokens = count_tokens(prompt, model), count_tokens(response, model)
    pricing = PRICING_PER_1K_TOKENS.get(model, PRICING_PER_1K_TOKENS["gpt-4o"])
    input_cost = input_tokens / 1000 * pricing["input"]
    output_cost = output_tokens / 1000 * pricing["output"]
    return {"input_tokens": input_tokens, "output_tokens": output_tokens,
            "input_cost": input_cost, "output_cost": output_cost,
            "total_cost": input_cost + output_cost}


def streaming_chatbot() -> None:
    from openai import OpenAI
    client, history = OpenAI(api_key=os.getenv("OPENAI_API_KEY")), []
    while True:
        user_msg = input("Bạn: ")
        if user_msg.strip().lower() in ("quit", "exit"):
            break
        stream = client.chat.completions.create(
            model=OPENAI_MODEL, messages=history + [{"role": "user", "content": user_msg}], stream=True)
        reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            reply += delta
        print()
        history.extend(({"role": "user", "content": user_msg}, {"role": "assistant", "content": reply}))
        history = history[-6:]


def retry_with_backoff(fn: Callable, max_retries: int = 3, base_delay: float = 0.1) -> Any:
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(base_delay * (2 ** attempt))


def run_assistant(persona: str, get_input: Callable[[], str] = None,
                  max_turns: int = None) -> dict:
    from openai import OpenAI
    get_input = get_input or input
    client, history, turns, tokens, cost = OpenAI(api_key=os.getenv("OPENAI_API_KEY")), [], 0, 0, 0.0
    while max_turns is None or turns < max_turns:
        user_msg = get_input()
        if user_msg.strip().lower() in ("quit", "exit"):
            break
        messages = [{"role": "system", "content": persona}] + history + [{"role": "user", "content": user_msg}]
        stream = retry_with_backoff(lambda: client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages, stream=True))
        reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            reply += delta
        print()
        history.extend(({"role": "user", "content": user_msg}, {"role": "assistant", "content": reply}))
        history = history[-6:]
        turns += 1
        tokens += count_tokens(user_msg) + count_tokens(reply)
        cost += estimate_cost(user_msg, reply)["total_cost"]
    return {"num_turns": turns, "total_tokens": tokens, "total_cost": cost, "history": history}


def batch_compare(prompts: list[str]) -> list[dict]:
    return [{"prompt": prompt, **compare_models(prompt)} for prompt in prompts]


def format_comparison_table(results: list[dict]) -> str:
    headers = ["Prompt", "GPT-4o Response", "Mini Response", "GPT-4o Latency", "Mini Latency"]
    rows = [" | ".join(headers), " | ".join(["---"] * len(headers))]
    def shorten(value: str) -> str:
        return value if len(value) <= 40 else value[:37] + "..."
    for result in results:
        rows.append(" | ".join([shorten(result["prompt"]), shorten(result["gpt4o_response"]),
                                shorten(result["mini_response"]), f'{result["gpt4o_latency"]:.2f}s',
                                f'{result["mini_latency"]:.2f}s']))
    return "\n".join(rows)
