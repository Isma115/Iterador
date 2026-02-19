import json
import os
import uuid
from datetime import datetime

class SessionManager:
    def __init__(self, storage_dir="saved_searches"):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def save_session(self, query, results, session_id=None):
        """Saves a search session to a JSON file."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"session_{session_id}.json"
        filepath = os.path.join(self.storage_dir, filename)

        data = {
            "id": session_id,
            "query": query,
            "timestamp": timestamp,
            "results": results
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        return session_id

    def load_session(self, filename):
        """Loads a session from a JSON file."""
        filepath = os.path.join(self.storage_dir, filename)
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_sessions(self):
        """Returns a list of saved sessions sorted by timestamp (newest first)."""
        sessions = []
        if not os.path.exists(self.storage_dir):
            return []

        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        sessions.append({
                            "filename": filename,
                            "query": data.get("query", "Sin título"),
                            "timestamp": data.get("timestamp", "Desconocido"),
                            "result_count": len(data.get("results", []))
                        })
                except Exception:
                    continue # Skip corrupted files
        
        # Sort by timestamp descending
        sessions.sort(key=lambda x: x["timestamp"], reverse=True)
        return sessions

    def delete_session(self, filename):
        """Deletes a session file."""
        filepath = os.path.join(self.storage_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
