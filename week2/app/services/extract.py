from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


# ============================================================
# TODO 1: LLM-Powered Action Item Extraction (AI-Generated)
# ============================================================

class ActionItems(BaseModel):
    """
    Pydantic model for structured output from Ollama.
    Defines the expected JSON schema for action items extraction.
    """
    items: List[str]


# System prompt for the LLM to extract action items
EXTRACTION_SYSTEM_PROMPT = """You are a helpful assistant that extracts action items from notes.

Your task is to:
1. Read the provided notes carefully
2. Identify all actionable tasks, to-dos, and action items
3. Extract them as a clean list of strings

Guidelines:
- Look for bullet points, checkboxes, numbered lists
- Look for keywords like "todo", "action", "next", "need to", "should", "must"
- Look for imperative sentences (e.g., "Fix the bug", "Update the docs")
- Remove any checkbox markers like "[ ]" or "[todo]" from the extracted items
- Each item should be a clear, actionable statement
- If no action items are found, return an empty list

Return ONLY the action items as a JSON array of strings."""


def extract_action_items_llm(text: str, model: str = "llama3.1:8b") -> List[str]:
    """
    Extract action items from text using Ollama LLM with structured output.
    
    This function uses Ollama's structured output feature to ensure the LLM
    returns properly formatted JSON that matches our ActionItems schema.
    
    :param text: The input text (notes) to extract action items from.
    :param model: The Ollama model to use (default: llama3.2).
    :return: A list of extracted action items as strings.
    
    AI-Generated: This function was generated with AI assistance for TODO 1.
    """
    # Handle empty input
    if not text or not text.strip():
        return []
    
    try:
        # Call Ollama with structured output format
        # The 'format' parameter accepts a Pydantic model to enforce JSON schema
        response = chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": EXTRACTION_SYSTEM_PROMPT
                },
                {
                    "role": "user", 
                    "content": f"Please extract all action items from the following notes:\n\n{text}"
                }
            ],
            format=ActionItems.model_json_schema()  # Structured output using Pydantic schema
        )
        
        # Parse the structured response
        response_content = response.message.content
        result = ActionItems.model_validate_json(response_content)
        
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: List[str] = []
        for item in result.items:
            # Clean up the item
            cleaned = item.strip()
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            unique.append(cleaned)
        
        return unique
        
    except Exception as e:
        # Log the error and fall back to empty list
        print(f"Error in LLM extraction: {e}")
        # Optionally fall back to rule-based extraction
        # return extract_action_items(text)
        return []

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
