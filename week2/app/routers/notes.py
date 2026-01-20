# ============================================================
# TODO 3: Refactored Notes Router (AI-Generated)
# ============================================================
"""
Router for notes management endpoints.
Uses Pydantic schemas for request/response validation.

AI-Generated: This file was refactored with AI assistance for TODO 3.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter

from .. import db
from ..schemas import (
    CreateNoteRequest,
    NoteResponse,
    NoteListResponse,
)
from ..exceptions import NotFoundError, ValidationError, DatabaseError


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(request: CreateNoteRequest) -> NoteResponse:
    """
    Create a new note.
    
    - **content**: The content of the note to create
    
    Returns the created note with its ID and timestamp.
    """
    content = request.content.strip()
    
    if not content:
        raise ValidationError("Content cannot be empty")
    
    try:
        note_id = db.insert_note(content)
        note = db.get_note(note_id)
        
        if note is None:
            raise DatabaseError("Failed to retrieve created note")
        
        return NoteResponse(
            id=note["id"],
            content=note["content"],
            created_at=note["created_at"],
        )
    except (ValidationError, DatabaseError):
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to create note: {str(e)}")


@router.get("", response_model=NoteListResponse)
def list_notes() -> NoteListResponse:
    """
    List all notes.
    
    Returns all notes ordered by creation date (newest first).
    """
    try:
        rows = db.list_notes()
        notes = [
            NoteResponse(
                id=r["id"],
                content=r["content"],
                created_at=r["created_at"],
            )
            for r in rows
        ]
        return NoteListResponse(notes=notes, total=len(notes))
    except Exception as e:
        raise DatabaseError(f"Failed to list notes: {str(e)}")


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """
    Get a specific note by ID.
    
    - **note_id**: The ID of the note to retrieve
    
    Returns the note if found, raises 404 if not.
    """
    try:
        row = db.get_note(note_id)
        
        if row is None:
            raise NotFoundError("Note", note_id)
        
        return NoteResponse(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get note: {str(e)}")


@router.delete("/{note_id}")
def delete_note(note_id: int) -> dict:
    """
    Delete a note by ID.
    
    - **note_id**: The ID of the note to delete
    
    Note: This also deletes associated action items.
    """
    try:
        row = db.get_note(note_id)
        
        if row is None:
            raise NotFoundError("Note", note_id)
        
        db.delete_note(note_id)
        return {"message": f"Note {note_id} deleted successfully"}
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to delete note: {str(e)}")
