import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_response(industry: str, style: str, goals: str):
    if not OPENAI_API_KEY:
        return "❌ Missing API key. Please set your OPENAI_API_KEY environment variable."

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",  # or "gpt-4o", depending on your plan
        "messages": [
            {"role": "system", "content": "You are a portfolio-building assistant."},
            {"role": "user", "content": f"""
Industry: {industry}
Preferred Style: {style}
Career Goals: {goals}

Generate specific advice for improving a personal portfolio to match these preferences.
"""}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        data = response.json()
    except Exception as e:
        return f"❌ Failed to parse API response: {str(e)}"

    # Debugging block – this helps us see what's wrong if it fails
    if "error" in data:
        return f"❌ OpenAI API error: {data['error'].get('message', 'Unknown error')}"

    if "choices" not in data:
        return f"❌ Unexpected API response: {data}"

    return data["choices"][0]["message"]["content"]
