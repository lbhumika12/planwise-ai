"""
PlanWise AI - AI Service
Handles LLM integration (OpenAI, Anthropic, Gemini) with deterministic fallback.
Never exposes secrets to the frontend.
"""
import json
import logging
from typing import Optional, List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are PlanWise AI, a focused and practical productivity assistant.
Your job is to help users manage tasks, prioritize work, and plan their day.

You ALWAYS respond with a JSON object in this exact format:
{
  "message": "Your helpful response text here",
  "intent": "one of: create_task|list_tasks|complete_task|update_task|delete_task|prioritize|generate_schedule|available_time|overdue_tasks|general",
  "action": null or {
    "action_type": "create_task|update_task|complete_task|delete_task",
    "task_data": {...},
    "requires_confirmation": true/false,
    "task_query": "search term to find existing task"
  },
  "suggested_prompts": ["prompt 1", "prompt 2"]
}

Rules:
- Be concise and practical. Focus on productivity.
- For create_task: extract title, due_date (YYYY-MM-DD), priority (low/medium/high/urgent), estimated_duration (minutes), category, description.
- For complete_task/delete_task: extract a task_query (search term) and set requires_confirmation=true for delete.
- For update_task: extract task_query and the fields to update.
- For schedule/prioritize: set action=null and provide helpful text. The schedule is computed by code.
- Never invent task data or pretend to execute operations. Only propose actions.
- If you're unsure about a date, include a note in the message.
- Keep your message friendly but brief.
- Always include 2-3 suggested_prompts relevant to what the user might ask next.
"""


async def call_ai(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    context: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Call the configured AI provider. Returns parsed JSON response or None.
    """
    provider = settings.active_ai_provider
    if not provider:
        return None

    full_message = message
    if context:
        full_message = f"Context about user's tasks:\n{context}\n\nUser message: {message}"

    messages = []
    if history:
        for h in history[-6:]:  # Only last 6 messages for context
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": full_message})

    try:
        if provider == "openai":
            return await _call_openai(messages)
        elif provider == "anthropic":
            return await _call_anthropic(messages)
        elif provider == "gemini":
            return await _call_gemini(messages)
    except Exception as e:
        logger.error(f"AI call failed ({provider}): {type(e).__name__}: {str(e)[:200]}")
        return None

    return None


async def _call_openai(messages: List[Dict]) -> Optional[Dict]:
    """Call OpenAI API."""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.3,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return None


async def _call_anthropic(messages: List[Dict]) -> Optional[Dict]:
    """Call Anthropic Claude API."""
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        prompt = SYSTEM_PROMPT + "\n\nAlways respond with valid JSON only."
        response = await client.messages.create(
            model=settings.anthropic_model,
            system=prompt,
            messages=messages,
            max_tokens=800,
        )
        content = response.content[0].text
        # Extract JSON from response
        json_match = content.strip()
        if json_match.startswith("```"):
            json_match = json_match.strip("`").strip("json").strip()
        return json.loads(json_match)
    except Exception as e:
        logger.error(f"Anthropic error: {e}")
        return None


async def _call_gemini(messages: List[Dict]) -> Optional[Dict]:
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            settings.gemini_model,
            system_instruction=SYSTEM_PROMPT + "\n\nAlways respond with valid JSON only.",
        )

        # Build conversation
        chat = model.start_chat(history=[])
        last_response = None
        for msg in messages:
            if msg["role"] == "user":
                last_response = chat.send_message(msg["content"])
            # Gemini handles alternating turns internally

        if last_response:
            content = last_response.text.strip()
            if content.startswith("```"):
                content = content.strip("`").strip("json").strip()
            return json.loads(content)
    except Exception as e:
        logger.error(f"Gemini error: {e}")
    return None


def get_ai_status() -> Dict[str, Any]:
    """Return current AI configuration status (no secrets)."""
    return {
        "available": settings.ai_available,
        "provider": settings.active_ai_provider,
        "mode": "ai_powered" if settings.ai_available else "rule_based",
    }
