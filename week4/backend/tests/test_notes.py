def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_delete_note(client):
    """Test DELETE /notes/{id} endpoint - TDD approach per CLAUDE.md"""
    # Step 1: Create a note first
    payload = {"title": "To Delete", "content": "This will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Step 2: Verify the note exists
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "To Delete"

    # Step 3: Delete the note
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204  # No Content on successful delete

    # Step 4: Verify the note no longer exists
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    """Test DELETE returns 404 for non-existent note"""
    r = client.delete("/notes/99999")
    assert r.status_code == 404


def test_update_note(client):
    """Test PUT /notes/{id} endpoint - TestAgent TDD"""
    # Step 1: Create a note first
    payload = {"title": "Original Title", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201
    note_id = r.json()["id"]

    # Step 2: Update the note
    update_payload = {"title": "Updated Title", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=update_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == note_id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"

    # Step 3: Verify the update persisted
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"
    assert r.json()["content"] == "Updated content"


def test_update_note_not_found(client):
    """Test PUT returns 404 for non-existent note"""
    update_payload = {"title": "New Title", "content": "New content"}
    r = client.put("/notes/99999", json=update_payload)
    assert r.status_code == 404


def test_update_note_partial(client):
    """Test PUT with partial update (only title or only content)"""
    # Create a note
    payload = {"title": "Original", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    note_id = r.json()["id"]

    # Update only title
    r = client.put(f"/notes/{note_id}", json={"title": "New Title", "content": "Original content"})
    assert r.status_code == 200
    assert r.json()["title"] == "New Title"
