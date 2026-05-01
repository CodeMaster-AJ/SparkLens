import json
import time
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior startup analyst with 20 years of experience evaluating early-stage startup ideas.

You MUST respond ONLY with a valid JSON object. No markdown. No backticks. No explanation. No text before or after the JSON.

The JSON must have EXACTLY these keys:
- summary: string (2-3 sentences, honest overview)
- verdict: exactly one of "GO", "CAUTION", "NO-GO"
- market_score: integer 1-10
- feasibility_score: integer 1-10
- strengths: array of exactly 4 strings
- weaknesses: array of exactly 4 strings
- opportunities: array of exactly 4 strings
- threats: array of exactly 4 strings
- risks: array of exactly 3 objects, each with keys "risk" (string) and "mitigation" (string)
- next_steps: array of exactly 5 strings, each starting with an action verb

Rules:
- Be specific to THIS idea. No generic advice.
- Be honest. If the idea has serious problems, say so.
- Each string should be 1-2 sentences max.
- verdict GO means strong potential, CAUTION means proceed carefully, NO-GO means fundamental problems exist."""


def build_user_prompt(submission):
    return f"""Analyse this startup idea:

Idea Title: {submission.title or 'Not provided'}
Description: {submission.description}
Target Audience: {submission.audience or 'Not specified'}
Industry: {submission.get_industry_display() if submission.industry else 'Not specified'}

Provide a thorough, honest analysis. Be specific."""


def call_openrouter(submission):
    """Call OpenRouter API and return parsed analysis dict. Raises ValueError on failure."""
    start = time.time()

    if not settings.OPENROUTER_API_KEY:
        raise ValueError("AI service is not configured. Please set OPENROUTER_API_KEY.")

    headers = {
        'Authorization': f'Bearer {settings.OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://sparklens.app',
        'X-Title': 'SparkLens',
    }

    payload = {
        'model': settings.OPENROUTER_MODEL,
        'max_tokens': 1500,
        'temperature': 0.7,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': build_user_prompt(submission)},
        ],
    }

    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=settings.OPENROUTER_TIMEOUT,
        )
        response.raise_for_status()
    except requests.Timeout:
        logger.error("OpenRouter timeout for submission %s", submission.id)
        raise ValueError("The AI took too long to respond. Please try again.")
    except requests.RequestException as e:
        logger.error("OpenRouter request failed: %s", e)
        raise ValueError("Could not reach the AI service. Please try again.")

    elapsed_ms = int((time.time() - start) * 1000)

    try:
        raw_content = response.json()['choices'][0]['message']['content'].strip()
        # Strip markdown code blocks if model wraps in them
        if raw_content.startswith('```'):
            raw_content = raw_content.split('```')[1]
            if raw_content.startswith('json'):
                raw_content = raw_content[4:]
        data = json.loads(raw_content)
    except (KeyError, json.JSONDecodeError) as e:
        logger.error("Failed to parse OpenRouter response: %s | Raw: %s", e, response.text[:500])
        raise ValueError("The AI returned an unexpected response. Please try again.")

    # Validate required keys
    required_keys = ['summary', 'verdict', 'market_score', 'feasibility_score',
                     'strengths', 'weaknesses', 'opportunities', 'threats', 'risks', 'next_steps']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"AI response missing field: {key}. Please try again.")

    # Normalise verdict
    verdict = str(data.get('verdict', '')).upper()
    if verdict not in ['GO', 'CAUTION', 'NO-GO']:
        verdict = 'CAUTION'

    # Clamp scores
    market_score = max(1, min(10, int(data.get('market_score', 5))))
    feasibility_score = max(1, min(10, int(data.get('feasibility_score', 5))))

    return {
        'verdict': verdict,
        'summary': str(data.get('summary', '')),
        'market_score': market_score,
        'feasibility_score': feasibility_score,
        'strengths': list(data.get('strengths', [])),
        'weaknesses': list(data.get('weaknesses', [])),
        'opportunities': list(data.get('opportunities', [])),
        'threats': list(data.get('threats', [])),
        'risks': list(data.get('risks', [])),
        'next_steps': list(data.get('next_steps', [])),
        'model_used': getattr(settings, 'MODEL_DISPLAY_NAME', 'IdeaPulse AI'),
        'generation_ms': elapsed_ms,
    }
