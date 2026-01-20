# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
Implement an extract_action_items_llm() function in week2/app/services/extract.py that uses Ollama 
local LLM with structured output to extract action items from user notes. Requirements:

1. Use Pydantic to define the output schema (ActionItems model with a list of strings)
2. Design an effective system prompt to guide the LLM in extracting action items
3. Use Ollama's structured output feature (format parameter with Pydantic model JSON schema)
4. Handle edge cases: empty input, LLM errors
5. Deduplicate the extracted items while preserving order
6. Use llama3.1:8b as the default model (available on my system)

The function should look for:
- Bullet points, checkboxes, numbered lists
- Keywords like "todo", "action", "next", "need to", "should", "must"  
- Imperative sentences (e.g., "Fix the bug", "Update the docs")

Reference documentation: https://ollama.com/blog/structured-outputs
``` 

Generated Code Snippets:
```
File: week2/app/services/extract.py

Lines 10: Added import for Pydantic BaseModel
  - from pydantic import BaseModel

Lines 15-23: ActionItems Pydantic model for structured output
  - class ActionItems(BaseModel):
  -     items: List[str]

Lines 26-43: EXTRACTION_SYSTEM_PROMPT constant
  - System prompt that guides the LLM to extract action items with specific guidelines

Lines 46-104: extract_action_items_llm() function
  - Main function that calls Ollama with structured output
  - Handles empty input (returns [])
  - Uses chat() with format=ActionItems.model_json_schema()
  - Parses response with ActionItems.model_validate_json()
  - Deduplicates results while preserving order
  - Error handling with try-except block
```

### Exercise 2: Add Unit Tests
Prompt: 
```
Write comprehensive unit tests for the extract_action_items_llm() function in 
week2/tests/test_extract.py. Requirements:

1. Use unittest.mock to mock the Ollama chat() function to avoid actual LLM calls during testing
2. Create a TestExtractActionItemsLLM test class with multiple test cases
3. Cover the following scenarios:
   - Bullet list input (- item format)
   - Keyword-prefixed lines (todo:, action:, next:)
   - Empty input (should return [] without calling LLM)
   - Numbered list input (1. item format)
   - Checkbox format input (- [ ] item)
   - Mixed format input
   - Deduplication (duplicate items should be removed)
   - LLM error handling (should return [] on exception)
   - Invalid JSON response handling
   - No action items found scenario

4. Each test should:
   - Have a descriptive name and docstring
   - Set up appropriate mock responses
   - Assert expected behavior
   - Use @patch decorator for mocking

5. Add clear comments indicating this is AI-generated code for TODO 2
``` 

Generated Code Snippets:
```
File: week2/tests/test_extract.py

Lines 3: Added imports for mocking
  - from unittest.mock import patch, MagicMock

Lines 5: Updated import to include extract_action_items_llm
  - from ..app.services.extract import extract_action_items, extract_action_items_llm

Lines 22-226: TestExtractActionItemsLLM test class with 10 test methods:
  - Lines 32-37: _create_mock_response() helper method
  - Lines 40-60: test_extract_bullet_list - Tests bullet list format
  - Lines 63-83: test_extract_keyword_prefixed - Tests todo:/action:/next: prefixes
  - Lines 86-95: test_extract_empty_input - Tests empty/whitespace/None input
  - Lines 98-117: test_extract_numbered_list - Tests numbered list format
  - Lines 120-139: test_extract_checkbox_format - Tests [ ] checkbox format
  - Lines 142-167: test_extract_mixed_format - Tests combined formats
  - Lines 170-185: test_extract_deduplication - Tests duplicate removal
  - Lines 188-198: test_extract_llm_error_handling - Tests exception handling
  - Lines 201-214: test_extract_invalid_json_handling - Tests malformed JSON
  - Lines 217-226: test_extract_no_action_items - Tests empty result

Test Results: All 11 tests passed (including 1 existing + 10 new tests)
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
Refactor the backend codebase to improve structure, type safety, and error handling. Tasks:

1. Create Pydantic schemas (app/schemas.py) for all API requests and responses to define clear contracts
2. Create specialized exception classes (app/exceptions.py) for consistent error handling
3. Centralize configuration (app/config.py) using environment variables
4. Refactor Routers (app/routers/*.py):
   - Use Pydantic models for request bodies and response models
   - Implement proper error handling using custom exceptions
   - Add docstrings and type hints
5. Refactor Main Application (app/main.py):
   - Implement an application factory pattern
   - Add lifecycle management (startup/shutdown events)
   - Register global exception handlers
   - Integrate configuration settings
6. Update Database Module (app/db.py):
   - Add helper functions for deleting notes and fetching single action items
   - Ensure consistent error handling

Goal: Make the codebase production-ready with validation, robust error handling, and maintainable structure.
``` 

Generated/Modified Code Snippets:
```
1. app/schemas.py (New File)
   - Defined Pydantic models: ExtractRequest, CreateNoteRequest, ActionItemResponse, NoteResponse, etc.
   - Added validation constraints and examples

2. app/config.py (New File)
   - Created Settings dataclass for configuration management
   - Implemented environment variable loading with dotenv
   - Added lru_cache for settings singleton

3. app/exceptions.py (New File)
   - Created base AppException and specific exceptions (NotFoundError, ValidationError, DatabaseError)
   - Standardized error response structure

4. app/routers/action_items.py (Refactored)
   - Updated endpoints to use Pydantic models
   - Added extract_action_items_llm integration
   - Improved error handling with try-except blocks
   - Added comprehensive docstrings

5. app/routers/notes.py (Refactored)
   - Updated endpoints to use Pydantic models
   - Added delete_note endpoint
   - Improved error handling and status codes

6. app/main.py (Refactored)
   - Implemented create_app factory and lifespan context manager
   - Added global exception handlers
   - Configured logging and static files
   
7. app/db.py (Modified)
   - Added delete_note() and get_action_item() functions
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
Using Agentic Mode, automate the integration of the new LLM extraction features into the frontend.
Tasks:
1. Update `frontend/index.html` to add:
   - An "Extract (LLM)" button that calls the POST /action-items/extract endpoint with use_llm=true
   - A "List Notes" button to view all saved notes
   - A notes display section to list saved notes
   - Delete functionality for notes
   - A styled UI with loading states and error handling

2. Verify the changes by creating an integration test script `test_integration.py` that simulates the frontend calls to the backend API, ensuring that:
   - LLM extraction works via API
   - Note listing works
   - Note deletion works
``` 

Generated Code Snippets:
```
File: week2/frontend/index.html
Lines 25-30: Added buttons container
  - Added "Extract (LLM)" and "List Notes" buttons with inline styles

Lines 33-38: Added extraction results and notes list sections
  - <div id="notes_section">...</div>

Lines 118-154: Added handleExtract function supporting LLM mode
  - Handles 'use_llm' parameter
  - Updates UI with loading state

Lines 160-220: Added loadNotes function
  - Fetches notes from /notes endpoint
  - Renders notes list with "Delete" and "View Action Items" buttons
  - Implements delete logic

Verification:
Created and ran `week2/test_integration.py` which successfully verified all API endpoints (Extract LLM, List Notes, Delete Note) using FastAPI TestClient with mocked LLM service.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
Analyze the entire codebase in the 'week2/' directory and generate a comprehensive README.md file. 
The README should include:
- A descriptive title and project overview
- Key features list (Rule-based vs LLM extraction, Note management)
- Technology stack details (FastAPI, Pydantic, SQLite, Ollama)
- Step-by-step installation and setup instructions
- Guide on how to run the application and tests
- API documentation overview
- Project structure explanation
``` 

Generated Code Snippets:
```
File: week2/README.md (New File)
- Generated a complete project documentation file including:
  - Project Overview
  - Features
  - Tech Stack
  - Getting Started (Prerequisites, Installation, Running)
  - API Documentation
  - Testing Instructions
  - Project Structure
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 