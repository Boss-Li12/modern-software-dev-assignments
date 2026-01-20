from fastapi.testclient import TestClient
from week2.app.main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_frontend_integration():
    with TestClient(app) as client:
        print("Testing 'Extract LLM' integration...")
        
        # Mock LLM response to avoid actual call
        with patch('week2.app.services.extract.chat') as mock_chat:
            mock_response = MagicMock()
            mock_response.message.content = '{"items": ["Mocked item 1", "Mocked item 2"]}'
            mock_chat.return_value = mock_response
            
            # 1. Test Extract LLM
            response = client.post(
                "/action-items/extract", 
                json={
                    "text": "Please do this.\n- Item 1\n- Item 2", 
                    "save_note": True, 
                    "use_llm": True
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["extraction_method"] == "llm"
            assert len(data["items"]) == 2
            print("✅ Extract LLM successful")
            
            note_id = data["note_id"]
            
        print("\nTesting 'List Notes' integration...")
        # 2. Test List Notes
        response = client.get("/notes")
        assert response.status_code == 200
        notes = response.json()["notes"]
        assert len(notes) > 0
        # Verify the note we just added is there
        found = any(n["id"] == note_id for n in notes)
        assert found
        print(f"✅ List Notes successful (found note {note_id})")
        
        print("\nTesting 'Delete Note' integration...")
        # 3. Test Delete Note
        response = client.delete(f"/notes/{note_id}")
        assert response.status_code == 200
        
        # Verify deletion
        response = client.get(f"/notes/{note_id}")
        assert response.status_code == 404
        print(f"✅ Delete Note successful (note {note_id} gone)")

if __name__ == "__main__":
    try:
        test_frontend_integration()
        print("\n🎉 All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
