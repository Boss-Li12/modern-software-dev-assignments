# ============================================================
# TODO 3: Pydantic Schemas for API Contracts (AI-Generated)
# ============================================================
"""
This module defines Pydantic models for request/response validation.
These schemas provide well-defined API contracts for the action item extractor.

AI-Generated: This file was created with AI assistance for TODO 3.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ====================
# Request Schemas
# ====================

class ExtractRequest(BaseModel):
    """Request body for extracting action items from text."""
    text: str = Field(..., min_length=1, description="The notes text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")
    use_llm: bool = Field(default=False, description="Whether to use LLM for extraction")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "- [ ] Set up database\n- Implement API\ntodo: Write tests",
                "save_note": True,
                "use_llm": False
            }
        }


class CreateNoteRequest(BaseModel):
    """Request body for creating a new note."""
    content: str = Field(..., min_length=1, description="The content of the note")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Meeting notes from today's standup..."
            }
        }


class MarkDoneRequest(BaseModel):
    """Request body for marking an action item as done/undone."""
    done: bool = Field(default=True, description="Whether the action item is done")


# ====================
# Response Schemas
# ====================

class ActionItemResponse(BaseModel):
    """Response model for a single action item."""
    id: int = Field(..., description="Unique identifier of the action item")
    text: str = Field(..., description="The action item text")
    note_id: Optional[int] = Field(None, description="Associated note ID if any")
    done: bool = Field(default=False, description="Whether the action item is completed")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class ExtractResponse(BaseModel):
    """Response model for action item extraction."""
    note_id: Optional[int] = Field(None, description="ID of the saved note if save_note was True")
    items: List[ActionItemResponse] = Field(default_factory=list, description="Extracted action items")
    extraction_method: str = Field(default="heuristic", description="Method used: 'heuristic' or 'llm'")


class NoteResponse(BaseModel):
    """Response model for a single note."""
    id: int = Field(..., description="Unique identifier of the note")
    content: str = Field(..., description="The note content")
    created_at: str = Field(..., description="Creation timestamp")


class NoteListResponse(BaseModel):
    """Response model for listing notes."""
    notes: List[NoteResponse] = Field(default_factory=list, description="List of notes")
    total: int = Field(..., description="Total number of notes")


class MarkDoneResponse(BaseModel):
    """Response model for marking action item done."""
    id: int = Field(..., description="Action item ID")
    done: bool = Field(..., description="New done status")


# ====================
# Error Schemas
# ====================

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")


class ValidationErrorDetail(BaseModel):
    """Detail for validation errors."""
    loc: List[str] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
