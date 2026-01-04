"""Simple local storage for user preferences and authentication."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Storage file location
STORAGE_DIR = Path.home() / ".smart_pool_v2"
STORAGE_FILE = STORAGE_DIR / "user_data.json"

# Session expiration: 30 days
SESSION_EXPIRY_DAYS = 30


class LocalStorage:
    """Simple local storage using JSON file."""
    
    @staticmethod
    def _ensure_storage_dir():
        """Create storage directory if it doesn't exist."""
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _load_data() -> Dict[str, Any]:
        """Load data from storage file."""
        LocalStorage._ensure_storage_dir()
        
        if not STORAGE_FILE.exists():
            return {}
        
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, return empty dict
            return {}
    
    @staticmethod
    def _save_data(data: Dict[str, Any]):
        """Save data to storage file."""
        LocalStorage._ensure_storage_dir()
        
        try:
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving data: {e}")
    
    @staticmethod
    def save_auth(user_id: str, email: str):
        """Save authentication data with current timestamp."""
        data = LocalStorage._load_data()
        data['auth'] = {
            'user_id': user_id,
            'email': email,
            'login_timestamp': datetime.now().isoformat()
        }
        LocalStorage._save_data(data)
    
    @staticmethod
    def get_auth() -> Optional[Dict[str, str]]:
        """Get authentication data if still valid (within 30 days)."""
        data = LocalStorage._load_data()
        
        if 'auth' not in data:
            return None
        
        auth = data['auth']
        login_timestamp_str = auth.get('login_timestamp')
        
        if not login_timestamp_str:
            return None
        
        try:
            login_timestamp = datetime.fromisoformat(login_timestamp_str)
            expiry_date = login_timestamp + timedelta(days=SESSION_EXPIRY_DAYS)
            
            # Check if session is still valid
            if datetime.now() > expiry_date:
                # Session expired, clear auth
                LocalStorage.clear_auth()
                return None
            
            return {
                'user_id': auth.get('user_id'),
                'email': auth.get('email')
            }
        except (ValueError, KeyError):
            return None
    
    @staticmethod
    def clear_auth():
        """Clear authentication data."""
        data = LocalStorage._load_data()
        if 'auth' in data:
            del data['auth']
            LocalStorage._save_data(data)
    
    @staticmethod
    def save_preference(key: str, value: Any):
        """Save a user preference."""
        data = LocalStorage._load_data()
        
        if 'preferences' not in data:
            data['preferences'] = {}
        
        data['preferences'][key] = value
        LocalStorage._save_data(data)
    
    @staticmethod
    def get_preference(key: str, default: Any = None) -> Any:
        """Get a user preference."""
        data = LocalStorage._load_data()
        return data.get('preferences', {}).get(key, default)
    
    @staticmethod
    def get_all_preferences() -> Dict[str, Any]:
        """Get all user preferences."""
        data = LocalStorage._load_data()
        return data.get('preferences', {})
    
    @staticmethod
    def save_preferences(preferences: Dict[str, Any]):
        """Save multiple preferences at once."""
        data = LocalStorage._load_data()
        data['preferences'] = preferences
        LocalStorage._save_data(data)

