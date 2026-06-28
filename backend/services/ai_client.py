from config import AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_PROVIDER


def complete(system_prompt: str, user_prompt: str) -> str:
    """Send a prompt to the configured AI provider and return the response text."""
    if AI_PROVIDER == "anthropic":
        return _anthropic(system_prompt, user_prompt)
    return _openai(system_prompt, user_prompt)


def _anthropic(system_prompt: str, user_prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=AI_API_KEY)
    message = client.messages.create(
        model=AI_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _openai(system_prompt: str, user_prompt: str) -> str:
    from openai import OpenAI
    kwargs: dict = {"api_key": AI_API_KEY}
    if AI_BASE_URL:
        kwargs["base_url"] = AI_BASE_URL
    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=AI_MODEL,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
