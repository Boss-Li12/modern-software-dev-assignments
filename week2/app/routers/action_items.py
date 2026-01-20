# ============================================================
# TODO 3: Refactored Action Items Router (AI-Generated)
# ============================================================
"""
Router for action item extraction and management endpoints.
Uses Pydantic schemas for request/response validation.

AI-Generated: This file was refactored with AI assistance for TODO 3.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Query

from .. import db
from ..schemas import (
    ExtractRequest,
    ExtractResponse,
    ActionItemResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..exceptions import ValidationError, NotFoundError, DatabaseError
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    """
    Extract action items from provided text.
    
    - **text**: The notes text to extract action items from
    - **save_note**: Whether to save the text as a note in the database
    - **use_llm**: Whether to use LLM-powered extraction (slower but smarter)
    
    Returns extracted action items with optional note_id if saved.
    """
    text = request.text.strip()
    
    if not text:
        raise ValidationError("Text cannot be empty")
    
    try:
        # Save note if requested
        note_id: Optional[int] = None
        if request.save_note:
            note_id = db.insert_note(text)
        
        # Extract action items using selected method
        if request.use_llm:
            items = extract_action_items_llm(text)
            extraction_method = "llm"
        else:
            items = extract_action_items(text)
            extraction_method = "heuristic"
        
        # Store action items in database
        ids = db.insert_action_items(items, note_id=note_id)
        
        # Build response
        action_items = [
            ActionItemResponse(id=item_id, text=item_text, note_id=note_id, done=False)
            for item_id, item_text in zip(ids, items)
        ]
        
        return ExtractResponse(
            note_id=note_id,
            items=action_items,
            extraction_method=extraction_method
        )
        
    except Exception as e:
        if isinstance(e, (ValidationError, NotFoundError)):
            raise
        raise DatabaseError(f"Failed to process extraction: {str(e)}")


@router.get("", response_model=List[ActionItemResponse])
def list_all(
    note_id: Optional[int] = Query(None, description="Filter by note ID")
) -> List[ActionItemResponse]:
    """
    List all action items, optionally filtered by note_id.
    
    - **note_id**: Optional filter to get action items for a specific note
    """
    try:
        rows = db.list_action_items(note_id=note_id)
        return [
            ActionItemResponse(
                id=r["id"],
                note_id=r["note_id"],
                text=r["text"],
                done=bool(r["done"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]
    except Exception as e:
        raise DatabaseError(f"Failed to list action items: {str(e)}")


@router.get("/{action_item_id}", response_model=ActionItemResponse)
def get_action_item(action_item_id: int) -> ActionItemResponse:
    """
    Get a specific action item by ID.
    
    - **action_item_id**: The ID of the action item to retrieve
    """
    try:
        rows = db.list_action_items()
        for r in rows:
            if r["id"] == action_item_id:
                return ActionItemResponse(
                    id=r["id"],
                    note_id=r["note_id"],
                    text=r["text"],
                    done=bool(r["done"]),
                    created_at=r["created_at"],
                )
        raise NotFoundError("Action item", action_item_id)
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get action item: {str(e)}")


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, request: MarkDoneRequest) -> MarkDoneResponse:
    """
    Mark an action item as done or undone.
    
    - **action_item_id**: The ID of the action item to update
    - **done**: Whether the action item should be marked as done
    """
    try:
        db.mark_action_item_done(action_item_id, request.done)
        return MarkDoneResponse(id=action_item_id, done=request.done)
    except Exception as e:
        raise DatabaseError(f"Failed to update action item: {str(e)}")
